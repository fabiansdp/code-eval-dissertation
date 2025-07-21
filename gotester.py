import hashlib
import hmac
import json
from urllib.parse import urlparse
import sympy as sp
import sys
import numpy as np
import tqdm
import re

from data import read_results, read_testcase, stream_jsonl, write_jsonl
# from evaluation import create_test_code
from pathlib import Path

import uuid
import subprocess
import os

def extract_testcases_value(text):
    # Use regex to extract the full assignment to `testcases = {...}`
    match = re.search(r"testcases\s*=\s*({.*})", text, re.DOTALL)
    if match:
        return match.group(1)
    return text

def python_type_to_go_type(value):
    if value is None:
        return "interface{}"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float64"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, bytes):
        return "[]byte"
    elif isinstance(value, list):
        if value:
            elem_type = python_type_to_go_type(value[0])
            return f"[]{elem_type}"
        else:
            return "[]interface{}"
    elif isinstance(value, tuple):
        if value:
            elem_type = python_type_to_go_type(value[0])
            return f"[]{elem_type}"  # could be struct in real usage
        else:
            return "[]interface{}"
    elif isinstance(value, set):
        if value:
            elem_type = python_type_to_go_type(next(iter(value)))
            return f"map[{elem_type}]bool"
        else:
            return "map[interface{}]bool"
    elif isinstance(value, dict):
        if value:
            first_val = next(iter(value.values()))
            val_type = python_type_to_go_type(first_val)
            return f"map[string]{val_type}"
        else:
            return "map[string]interface{}"
    elif isinstance(value, BaseException):
        return "error"
    else:
        return "interface{}"

def python_to_go(value):
    if isinstance(value, list):
        # Convert list to Go slice
        return f"{python_type_to_go_type(value)}" + "{" + ", ".join(python_to_go(v) for v in value) + "}"
    elif isinstance(value, dict):
        items = []
        for k, v in value.items():
            key_str = f'"{k}"'
            val_str = python_to_go(v)
            items.append(f'{key_str}: {val_str}')
        return f"{python_type_to_go_type(value)}" + "{" + ", ".join(items) + "}"
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, Exception):
        return f'errors.New({str(value)})'
    elif value is None:
        return "nil"
    else:
        return str(value)
    
def create_arguments(args: dict) -> str:
    argument = "("
    index = 0
    for key in args:
        argument += f'{python_to_go(args[key])}'
        if index != len(args) -1 :
            argument += ","
        index += 1
    
    argument += ")"

    return argument

def get_expected_value(val, type):
    ex_out = python_to_go(val)

    if type == "string" and val is None:
        ex_out = str('""')

    return ex_out

def generate_go_tests(testcases: list, func_name: str, returns: list) -> str:
    output = []

    try:
        localdict = {}
        exec(testcases, globals(), localdict)
        extracted_tcs = localdict["testcases"]
    except Exception as e:
        print(e)
        return ""
    
    retVar = []
    for i in range(len(returns)):
        if returns[i] == "error":
            retVar.append(f"err")
        else:
            retVar.append(f"var{i}")

    output.append(f"func Test{func_name[0].upper() + func_name[1:]}(t *testing.T) {{")
    idx = 0
    for args, expected in extracted_tcs["capability"]:
        arguments = create_arguments(args)
        # print(arguments)
        func_call = ""
        if len(returns) > 0:
            ext_out = get_expected_value(expected, returns[0])
            func_call += f'\t{",".join(retVar)}'
            if idx == 0:
                func_call += ' := '
            else:
                func_call += ' = '

        func_call += f'{func_name}{arguments}'
        output.append(func_call)

        if len(returns) > 0:
            if isinstance(expected, Exception):
                output.append(f'\tassert.Error(t, err)')
            elif "error" in returns:
                output.append(f'\tassert.NoError(t, err, "should be %v", {ext_out})')

            if ext_out == "nil":
                output.append('\tassert.Nil(t, var0)')
            elif "*" in returns[0]:
                output.append(f'\texpected{idx} := {ext_out}')
                output.append(f'\tassert.Equal(t, &expected{idx}, var0)\n')
            else:
                output.append(f'\tassert.Equal(t, {ext_out}, var0)\n')
        idx += 1
        
    output.append("}\n")

    return "\n".join(output)

def insert_import(go_code: str, import_name: str) -> str:
    lines = go_code.splitlines()
    output_lines = []
    inserted = False

    for i, line in enumerate(lines):
        output_lines.append(line)
        if "package" in line.strip():
            # Check the next non-empty line for existing import "testing"
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip() == f'import "{import_name}"':
                inserted = True
            if not inserted:
                output_lines.append(f'import "{import_name}"')
                inserted = True

    return "\n".join(output_lines)

def remove_main_function(go_code):
    lines = go_code.splitlines()
    output = []
    inside_main = False
    brace_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not inside_main and stripped.startswith("func main()"):
            # Found the start of main function
            inside_main = True
            # Count braces to find end of block
            brace_count += line.count('{') - line.count('}')
        elif inside_main:
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                inside_main = False  # End of main reached
        else:
            output.append(line)

        i += 1

    return "\n".join(output).strip()

def extract_go_code(text):
    lines = text.splitlines()
    go_code_started = False
    go_code = []

    for line in lines:
        if line.strip().startswith("package main"):
            go_code_started = True
        if go_code_started:
            go_code.append(line)

    return "\n".join(go_code).strip()

# Pattern to match Go function definitions and capture their return type(s)
def parseRetToList(args: str) -> list:
    result = []

    if args.startswith("(") and args.endswith(")"):
        extract = args[1:-1].split(", ")
        result.extend(t.strip() for t in extract if t.strip())
    else:
        result.append(args)

    return result

def extract_return_types(code, function_name) -> list:
    pattern = rf'func\s+{re.escape(function_name)}\s*\([^)]*\)\s*({{[^}}]*}}|\([^)]+\)|[^\n{{]+)\s*\{{'

    match = re.search(pattern, code)
    if match:
        ret = match.group(1).strip()
        if ret.endswith('{'):
            ret = ret[:-1].strip()
        return parseRetToList(ret)
    else:
        return []


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# main()