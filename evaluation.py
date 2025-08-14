from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Union, Iterable, Dict
import itertools
import argparse

import numpy as np
import tqdm
import subprocess

from data import read_results, read_testcase, stream_jsonl, write_jsonl
from execution import check_correctness, get_tcs
from gotester import generate_go_tests, extract_return_types, insert_import, cd, clean_go_package_declaration
from pathlib import Path, PosixPath


def estimate_pass_at_k(
    num_samples: Union[int, List[int], np.ndarray],
    num_correct: Union[List[int], np.ndarray],
    k: int
) -> np.ndarray:
    """
    Estimates pass@k of each problem and returns them in an array.
    """

    def estimator(n: int, c: int, k: int) -> float:
        """
        Calculates 1 - comb(n - c, k) / comb(n, k).
        """
        if n - c < k:
            return 1.0
        return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

    if isinstance(num_samples, int):
        num_samples_it = itertools.repeat(num_samples, len(num_correct))
    else:
        assert len(num_samples) == len(num_correct)
        num_samples_it = iter(num_samples)

    return np.array([estimator(int(n), int(c), k) for n, c in zip(num_samples_it, num_correct)])


def create_test_code(
    setup: str, 
    result: str, 
    test: str, 
    function_name: str, 
    language: str
):
    if language == "python":
        return f"""from rapidfuzz import fuzz
{setup}
{result}
"""
# {test}
    
# """
# tcs = []
# for tc in testcases:
#     tcs.append({
#     "kwargs": tc[0],
#     "output": tc[1]
#     })
# """ + f"""
# """
# exceptions = []
# for item in tcs:
#     try:
#         output = {function_name}(**item["kwargs"])
#         if isinstance(output, str):
#             output = output.rstrip()
#             item["output"] = item["output"].rstrip()

#         assert output == item["output"]
#     except AssertionError as ae:
#         if isinstance(item["output"], str):
#             ratio = fuzz.partial_ratio(item["output"], output)
#             if ratio < 80:
#                 exceptions.append(ae)
#         else:
#             exceptions.append(ae)

#     except Exception as e:
#         if type(e) == type(item["output"]):
#             continue
#         else:
#             exceptions.append(e)

# if len(exceptions) > 0:
#     raise ExceptionGroup("there were problems", exceptions)    
    
    if language == "go":
        return f"""{setup}
{result}

{test}
"""

def evaluate_functional_correctness(
    sample_file: str,
    testcase: str,
    out_file: str,
    k: List[int] = [1, 3, 5],
    n_workers: int = 4,
    timeout: float = 3.0,
    language: str = "python"
):
    tcs = read_testcase(testcase)
    samples = read_results(sample_file)

    print(len(tcs))
    # Check the generated samples against test suites.
    with ThreadPoolExecutor(max_workers=2) as executor:

        futures = []
        completion_id = Counter()
        results = defaultdict(list)

        print("Reading samples...")
        idx = 0
        for task_id in tqdm.tqdm(tcs):
            if task_id not in samples:
                continue
            
            idx+= 1
            for sample in samples[task_id]:
                setup = ""
                if language == "python":
                    if tcs[task_id]["setup"] not in sample:
                        setup = tcs[task_id]["setup"] + "\n\n"

                result = sample
                test = tcs[task_id]["tc"]
                function_name = tcs[task_id]["function_name"]

                if language == "go":
                    returns = extract_return_types(result, function_name)
                    test = generate_go_tests(test, function_name, returns)
                    if "package main" not in sample:
                        setup = tcs[task_id]["setup"] + "\n\n"

                check_program = create_test_code(setup=setup, result=result, test=test, function_name=function_name, language=language)
                if language == "go":
                    check_program = clean_go_package_declaration(check_program)

                testcases = []
                try:
                    testcases = get_tcs(test)
                except Exception as e:
                    print(e, task_id)
#                     print(f"""{test}""" + """
# tcs = []
# for tc in testcases:
#     tcs.append({
#         "kwargs": tc[0],
#         "output": tc[1]
#     })
# """)
#                     print(test)
                    continue

                args = {
                    "sample": {
                        "task_id": task_id,
                        "function_name": function_name,
                        "test_code": check_program,
                    },
                    "testcases": testcases,
                    "is_func_correct": True if f"{function_name}" in result else False,
                    "language": language,
                    "timeout": timeout,
                    "completion_id": completion_id[task_id]
                }

                future = executor.submit(check_correctness, **args)
                futures.append(future)
                completion_id[task_id] += 1

        print("Running test suites...")
        for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
            result = future.result(timeout=10)
            results[result["task_id"]].append((result["completion_id"], result))

    # Calculate pass@k.
    total, correct = [], []
    for result in results.values():
        result.sort()
        passed = [r[1]["passed"] for r in result]
        total.append(len(passed))
        correct.append(sum(passed))
    
    total = np.array(total)
    correct = np.array(correct)
    ks = k
    pass_at_k = {f"pass@{k}": estimate_pass_at_k(total, correct, k).mean()
                 for k in ks if (total >= k).all()}

    # Finally, save the results in one file:
    def combine_results():
        for sample in stream_jsonl(testcase):
            task_id = sample["id"]
            if task_id not in results:
                continue

            for i in range (len(results[task_id])):
                if "results" not in results[task_id][i][1]:
                    print("No results key: ", results[task_id][i][1], " ", task_id)
                    continue

                for j in range (len(results[task_id][i][1]["results"])):
                    if "result" not in results[task_id][i][1]["results"][j]:
                        print("No result key: ", results[task_id][i][1]["results"][j], " ", task_id)
                        continue

                    if isinstance(results[task_id][i][1]["results"][j]["result"], Exception):
                        results[task_id][i][1]["results"][j]["exception"]= f"{type(results[task_id][i][1]['results'][j]['result'])}"
                        results[task_id][i][1]["results"][j]["result"]= str(results[task_id][i][1]['results'][j]['result'])

            result_arr = []
            for item in results[task_id]:
                if "results" in item[1]:
                    result_arr.append(item[1]["results"])
            
            stat_arr = []
            for item in results[task_id]:
                if "statistics" in item[1]:
                    stat_arr.append(item[1]["statistics"])
            
            passed_arr = []
            for item in results[task_id]:
                if "passed" in item[1]:
                    passed_arr.append(item[1]["passed"])
            
            yield {
                "task_id": task_id,
                "cwe_id": sample["CWE_ID"],
                "results": result_arr,
                "statistics": stat_arr,
                "passed": passed_arr,
            }

    print(f"Writing results to {out_file}...")
    write_jsonl(out_file, tqdm.tqdm(combine_results()))

    return {
        "pass_at_k": pass_at_k,
    }

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-tc", "--testcase", type=str)
    parser.add_argument("-r", "--results", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-l", "--language", type=str, default="python")

def main():
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    args = parser.parse_args()
    results = evaluate_functional_correctness(sample_file=args.results, testcase=args.testcase, out_file=args.output, language=args.language, timeout=60)
    print(results)

if __name__ == "__main__":
    main()
