from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Union, Iterable, Dict
import itertools
import argparse

import numpy as np
import tqdm
import subprocess

from data import read_results, read_testcase, stream_jsonl, write_jsonl
from execution import check_correctness
from gotester import generate_go_tests, extract_return_types, insert_import, cd
from pathlib import Path


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

{test}
""" + """
tcs = []
for tc in testcases['capability']:
    tcs.append({
    "kwargs": tc[0],
    "output": tc[1]
    })
""" + f"""
exceptions = []
for item in tcs:
    try:
        output = {function_name}(**item["kwargs"])
        if isinstance(output, str):
            output = output.rstrip()
            item["output"] = item["output"].rstrip()
        assert output == item["output"], item["output"] + " not " + output
    except AssertionError as ae:
        ratio = fuzz.partial_ratio(item["output"], output)
        if ratio < 80:
            exceptions.append(ae)
    except ValueError as ve:
        if item["output"] != ValueError:
            exceptions.append(ve)
    except Exception as e:
        print(e)
        exceptions.append(e)

if len(exceptions) > 0:
    raise ExceptionGroup("there were problems", exceptions)    
"""
    
    if language == "go":
        return f"""{setup}
{result}

{test}
"""

def evaluate_functional_correctness(
    sample_file: str,
    testcase: str,
    out_file: str,
    k: List[int] = [1, 10, 100],
    n_workers: int = 4,
    timeout: float = 3.0,
    language: str = "python"
):
    tcs = read_testcase(testcase)
    samples = read_results(sample_file)

    # Check the generated samples against test suites.
    with ThreadPoolExecutor(max_workers=n_workers) as executor:

        futures = []
        completion_id = Counter()
        n_samples = 0
        results = defaultdict(list)

        print("Reading samples...")
        index = 0
        for task_id in tqdm.tqdm(tcs):
            if task_id not in samples:
                continue
        
            setup = ""
            # if tcs[task_id]["setup"] not in samples[task_id]:
            #     setup = tcs[task_id]["setup"] + "\n\n"

            result = samples[task_id]
            test = tcs[task_id]["tc"]
            function_name = tcs[task_id]["function_name"]

            if language == "go":
                if f"func {function_name}" not in result:
                    print("Mismatched function name: ", function_name)
                    continue
                
                returns = extract_return_types(result, function_name)
                test = generate_go_tests(test, function_name, returns)
                if "package main" not in samples[task_id]:
                    setup = tcs[task_id]["setup"] + "\n\n"

            check_program = create_test_code(setup=setup, result=result, test=test, function_name=function_name, language=language)

            args = {
                "sample": {
                    "task_id": task_id,
                    "test_code": check_program
                },
                "language": language,
                "timeout": timeout,
                "completion_id": completion_id[task_id]
            }

            future = executor.submit(check_correctness, **args)
            futures.append(future)
            completion_id[task_id] += 1
            n_samples += 1
            index += 1

        print("Running test suites...")
        for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
            result = future.result()
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
        for sample in stream_jsonl(sample_file):
            task_id = sample["id"]
            if task_id not in results:
                continue

            result = results[task_id].pop(0)
            if type(result[1]["result"]) == ExceptionGroup:
                sample["result"] = ", ".join([f"{type(e)}: {str(e)}" for e in result[1]["result"].exceptions])
            elif type(result[1]["result"] == Exception):
                sample["result"] = str(result[1]["result"])
            else:
                sample["result"] = result[1]["result"]
            
            sample["passed"] = result[1]["passed"]
            yield sample

    print(f"Writing results to {out_file}...")
    write_jsonl(out_file, tqdm.tqdm(combine_results(), total=n_samples))

    return {
        "pass_at_k": pass_at_k,
        "num_samples": len(total),
        "num_success": np.count_nonzero(correct == 1)
    }

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-tc", "--testcase", type=str)
    parser.add_argument("-r", "--results", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-l", "--language", type=str, default="python")

# def main():
#     parser = argparse.ArgumentParser()
#     setup_parser(parser)
#     args = parser.parse_args()
#     results = evaluate_functional_correctness(sample_file=args.results, testcase=args.testcase, out_file=args.output, language=args.language, timeout=60)
#     print(results)

def main():
    tcs = read_testcase("dataset/seccode-go-gpt.jsonl")
    samples = read_results("results/go-deepseekcoder-7b.jsonl")
    
    for task_id in tcs:
        if task_id not in samples:
            continue

        setup = tcs[task_id]["setup"]
        # if "package main" not in samples[task_id]:
        #     setup = tcs[task_id]["setup"] + "\n\n"

        result = samples[task_id]
        # test = tcs[task_id]["tc"]
        # function_name = tcs[task_id]["function_name"]

        # if f"func {function_name}" not in result:
        #     print("Mismatched function name: ", function_name)
        #     # print("Salah goblok nama fungsinya")
        #     # print(function_name)
        #     # print(result)
        #     continue

        # returns = extract_return_types(result, function_name)
        # print(setup)

        # return
        # tc = generate_go_tests(test, function_name, returns)

        # check_program = create_test_code(setup=setup, result=result, test=tc, function_name=function_name, language="go")
        check_program = f"""{setup}"""
        # check_program = insert_import(check_program, "testing")
        # check_program = insert_import(check_program, "github.com/stretchr/testify/assert")
        go_dir = f"go-eval/{task_id}"
        go_file_name = f"{go_dir}.go"
        # Path(go_dir).mkdir(parents=True, exist_ok=True)

        with open(go_file_name, 'w') as go_file:
            go_file.write(check_program)

#         with open(f"{go_dir}/go.mod", "w") as go_mod:
#             go_mod.write("""module test.com

# go 1.24.5

# require github.com/stretchr/testify v1.10.0

# require (
# 	github.com/davecgh/go-spew v1.1.1 // indirect
# 	github.com/pmezard/go-difflib v1.0.0 // indirect
# 	gopkg.in/yaml.v3 v3.0.1 // indirect
# )
# """)

#         with open(f"{go_dir}/go.sum", 'w') as go_sum:
#             go_sum.write("""github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
# github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
# github.com/pmezard/go-difflib v1.0.0 h1:4DBwDE0NGyQoBHbLQYPwSUPoCMWR5BEzIk/f1lZbAQM=
# github.com/pmezard/go-difflib v1.0.0/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
# github.com/stretchr/testify v1.10.0 h1:Xv5erBjTwe/5IxqUQTdXv5kgmIvbHo3QQyRwhJsOfJA=
# github.com/stretchr/testify v1.10.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
# gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405 h1:yhCVgyC4o1eVCa2tZl7eS0r+SDo693bJlVdllGtEeKM=
# gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
# gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
# gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
# """) 

#         # enter the directory like this:
#         with cd(f"{go_dir}"):
#             subprocess.run("go mod tidy", shell=True)
#             subprocess.run("gopls codeaction -exec -w code_test.go", shell=True)
#             compile_res = subprocess.run("go test", check=False, capture_output=True, text=True, shell=True)
#             if compile_res.returncode != 0:
#                 print(compile_res.stdout)
#                 print(compile_res.stderr.strip())
#             else:
#                 print(compile_res.stdout)

#         break

if __name__ == "__main__":
    main()
