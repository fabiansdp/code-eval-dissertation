import contextlib
import signal
import math
import numpy as np
import json
import sys
import requests
import sympy
import argparse
import fastapi
import markdown
import markdownify
import markupsafe
import html

from data import read_results, read_testcase
from tqdm import tqdm
from rapidfuzz import fuzz

class TimeoutException(Exception):
    pass

def compute_pass_k(n, c, k):
    if c == 0:
        return 0
    if k > n:
        return 1.0
    return 1.0 - (math.comb(n-c,k)/math.comb(n,k))

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-tc", "--testcase", type=str)
    parser.add_argument("-r", "--results", type=str)

@contextlib.contextmanager
def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    args = parser.parse_args()

    tcs = read_testcase(args.testcase)
    results = read_results(args.results)
    num_samples = 0
    num_success = 0

    for task_id in tqdm(tcs):
        if task_id not in results:
            continue

        shared_globals = {
            "__builtins__": __builtins__,
            "numpy": np,
            "json": json,
            "sys": sys,
            "requests": requests,
            "sympy": sympy,
            "rapidfuzz": fuzz,
            "fastapi": fastapi,
            "markdownify": markdownify,
            "markupsafe": markupsafe,
            "markdown": markdown,
            "html": html
        }
        num_samples += 1

        setup = ""
        if tcs[task_id]["setup"] not in results[task_id]:
            setup = tcs[task_id]["setup"] + "\n\n"

        results[task_id] = results[task_id].replace("```", "")

        check_program = f"""from rapidfuzz import fuzz
{setup}
{results[task_id]}

{tcs[task_id]["tc"]}
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
        output = {tcs[task_id]["function_name"]}(**item["kwargs"])
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
        try:
            with time_limit(seconds=3):
                # print(check_program)
                exec(check_program, shared_globals)
                num_success += 1
        except ExceptionGroup as eg:
            print("|||||||||||||||||||||||")
            print(task_id)
            print(eg.exceptions)
            print("|||||||||||||||||||||||")
            continue
        except Exception as e:
            print("|||||||||||||||||||||||")
            print(task_id)
            print(e)
            print("|||||||||||||||||||||||")
            continue

    print(args.results)
    print("Total samples: ", num_samples)
    print("Total success: ", num_success)

if __name__ == "__main__":
    main()