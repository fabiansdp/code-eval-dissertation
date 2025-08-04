from typing import Optional, Dict
from gotester import insert_import, cd
from pathlib import Path

import ast
import contextlib
import faulthandler
import io
import os
import multiprocessing
import platform
import signal
import tempfile
import subprocess
import uuid

import multiprocessing
import subprocess
import uuid
import os
import shutil

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

from rapidfuzz import fuzz
from ctx import create_tempdir, reliability_guard, swallow_io, time_limit, TimeoutException

def unsafe_execute(sample, language, timeout, result):
    """
    This function is used to run the test code provided in the sample. It is
    called by the check_correctness function.
    
    :param sample: A dictionary containing the test code and other information.
    :param language: The programming language of the completion (python, java, or cpp).
    :param timeout: Time limit for execution (default 5 seconds).
    :param result: A shared list to store the result of the execution.
    """
    with create_tempdir():
        unique_id = f"{sample.get('task_id', 'task')}_{uuid.uuid4().hex[:8]}"

        if language == "python":
            # These system calls are needed when cleaning up tempdir.
            import os
            import shutil
            
            rmtree = shutil.rmtree
            rmdir = os.rmdir
            chdir = os.chdir

            reliability_guard()
            
            try:
                with swallow_io():
                    with time_limit(timeout):
                        exec(sample["test_code"], globals())
                result.append("passed")
            except TimeoutException:
                result.append("timed out")
            except ExceptionGroup as e:
                result.append(e)
            except Exception as e:
                result.append(e)

            shutil.rmtree = rmtree
            os.rmdir = rmdir
            os.chdir = chdir

        elif language == "go":
            sample["test_code"] = insert_import(sample["test_code"], "testing")
            sample["test_code"] = insert_import(sample["test_code"], "github.com/stretchr/testify/assert")

            go_dir = f"go-eval/{sample['task_id']}"
            go_file_name = f"{go_dir}/code_test.go"
            Path(go_dir).mkdir(parents=True, exist_ok=True)

            with open(f"{go_dir}/go.mod", "w") as go_mod:
                go_mod.write("""module test.com

go 1.24.4

require github.com/stretchr/testify v1.10.0

require (
	github.com/davecgh/go-spew v1.1.1 // indirect
	github.com/pmezard/go-difflib v1.0.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)
""")

            with open(f"{go_dir}/go.sum", 'w') as go_sum:
                go_sum.write("""github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/pmezard/go-difflib v1.0.0 h1:4DBwDE0NGyQoBHbLQYPwSUPoCMWR5BEzIk/f1lZbAQM=
github.com/pmezard/go-difflib v1.0.0/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
github.com/stretchr/testify v1.10.0 h1:Xv5erBjTwe/5IxqUQTdXv5kgmIvbHo3QQyRwhJsOfJA=
github.com/stretchr/testify v1.10.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405 h1:yhCVgyC4o1eVCa2tZl7eS0r+SDo693bJlVdllGtEeKM=
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
""") 

            with open(go_file_name, 'w') as go_file:
                go_file.write(sample["test_code"]) 

            # enter the directory like this:
            with cd(f"{go_dir}"):
                subprocess.run("go mod init test.com", shell=True)
                subprocess.run("go mod tidy", shell=True)
                subprocess.run("gopls codeaction -exec -w code_test.go", shell=True)
                exec_res = subprocess.run("go test", check=False, capture_output=True, text=True, shell=True)
                if exec_res.returncode == 0:
                    result.append("passed")
                else:
                    result.append(f"output: {exec_res.stdout.strip()}, failed: {exec_res.stderr.strip()}")

        elif language == "cpp":
            cpp_file_name = f"{unique_id}.cpp"
            executable = f"./{unique_id}"
            with open(cpp_file_name, 'w') as cpp_file:
                cpp_file.write("")
            
            try:
                compile_command = ["g++", cpp_file_name, "-o", unique_id]
                compile_res = subprocess.run(compile_command, check=False, timeout=timeout, capture_output=True, text=True)
                if compile_res.returncode != 0:
                    result.append(f"failed to compile: {compile_res.stderr.strip()}")
                else:
                    run_command = [executable]
                    exec_res = subprocess.run(run_command, check=False, timeout=timeout, capture_output=True, text=True)
                    if exec_res.returncode == 0:
                        result.append("passed")
                    else:
                        result.append(f"failed: {exec_res.stderr.strip()}")
            except subprocess.TimeoutExpired:
                result.append("timed out")
            except Exception as e:
                result.append(f"failed: {str(e)}")

        else:
            result.append(f"failed: Unsupported language {language}")

def check_correctness(sample: Dict, language: str, timeout: float = 5.0,
                      completion_id: Optional[int] = None) -> Dict:
    """
    Evaluates the functional correctness of a completion by running the test
    code provided in the sample.

    :param sample: A dictionary containing the test code and other information.
    :param language: The programming language of the completion (python, java, or cpp).
    :param timeout: Time limit for execution (default 5 seconds).
    :param completion_id: An optional completion ID for result matching.
    """
    manager = multiprocessing.Manager()
    result = manager.list()

    p = multiprocessing.Process(target=unsafe_execute, args=(sample, language, timeout, result))
    p.start()
    p.join(timeout=timeout + 1)
    if p.is_alive():
        p.kill()

    if not result:
        result.append("timed out")

    output = {
        "passed": result[0] == "passed",
        "result": result[0],
        "completion_id": completion_id
    }
    
    if "task_id" in sample:
        output["task_id"] = sample["task_id"]

    return output