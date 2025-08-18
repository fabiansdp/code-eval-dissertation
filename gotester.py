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
from pathlib import Path, PosixPath

import uuid
import subprocess
import os

def extract_testcases_value(text):
    # Use regex to extract the full assignment to `testcases = {...}`
    match = re.search(r"testcases\s*=\s*({.*})", text, re.DOTALL)
    if match:
        return match.group(1)
    return text

# def python_to_go(value):
#     if isinstance(value, list):
#         # Convert list to Go slice
#         return f"{python_type_to_go_type(value)}" + "{" + ", ".join(python_to_go(v) for v in value) + "}"
#     elif isinstance(value, dict):
#         items = []
#         for k, v in value.items():
#             key_str = f'"{k}"'
#             val_str = python_to_go(v)
#             items.append(f'{key_str}: {val_str}')
#         return f"{python_type_to_go_type(value)}" + "{" + ", ".join(items) + "}"
#     elif isinstance(value, str):
#         return f'"{value}"'
#     elif isinstance(value, bool):
#         return "true" if value else "false"
#     elif isinstance(value, bytes):
#         go_bytes = ", ".join(f"0x{byte:02x}" for byte in value)
#         return f"[]byte{{{go_bytes}}}"
#     elif isinstance(value, int) or isinstance(value, float):
#         return f'{value}'
#     elif isinstance(value, Exception):
#         return f'errors.New("{str(value)}")'
#     elif value is None:
#         return "nil"
#     else:
#         return f'"{str(value)}"'

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
    
def python_to_go(value, expected_type=None):
    if value is None:
        return "nil"

    if expected_type:
        if expected_type == "string":
            return f'"{value}"'
        elif expected_type in ("int", "int32", "int64", "float32", "float64"):
            return str(value)
        elif expected_type == "bool":
            return "true" if value else "false"
        elif expected_type == "[]byte":
            go_bytes = ", ".join(f"0x{byte:02x}" for byte in value)
            return f"[]byte{{{go_bytes}}}"
        elif expected_type.startswith("[]"):
            inner_type = expected_type[2:]
            return f"{expected_type}{{" + ", ".join(python_to_go(v, inner_type) for v in value) + "}}"
        elif expected_type.startswith("map["):
            # Find the closing bracket of the key type
            start = expected_type.find("[")
            end = expected_type.find("]", start)
            inner_type = expected_type[end+1:]
            items = []

            if isinstance(value, dict):
                pairs = value.items()
            
            if isinstance(value, tuple):
                pairs = value

            else:
                pairs = tuple()

            for k, v in pairs:
                key_str = f'"{k}"'  # assuming string keys
                val_str = python_to_go(v, inner_type)
                items.append(f"{key_str}: {val_str}")
            return f"{expected_type}{{" + ", ".join(items) + "}}"
        elif expected_type == "error":
            return f'errors.New("{str(value)}")'
        else:
            return f'"{str(value)}"'

    # fallback if no expected_type
    if isinstance(value, list):
        return f"{python_type_to_go_type(value)}" + "{" + ", ".join(python_to_go(v) for v in value) + "}"
    elif isinstance(value, dict):
        items = []
        for k, v in value.items():
            key_str = f'"{k}"'
            val_str = python_to_go(v)
            items.append(f"{key_str}: {val_str}")
        return f"{python_type_to_go_type(value)}" + "{" + ", ".join(items) + "}"
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, bytes):
        go_bytes = ", ".join(f"0x{byte:02x}" for byte in value)
        return f"[]byte{{{go_bytes}}}"
    elif isinstance(value, (int, float)):
        return f"{value}"
    elif isinstance(value, Exception):
        return f'errors.New("{str(value)}")'
    else:
        return f'"{str(value)}"'

    
def create_arguments(args: dict, arg_types: list) -> str:
    argument = "("
    index = 0
    arg_len = len(arg_types)
    for key in args:
        arg_type = None
        if index < arg_len:
            arg_type = arg_types[index]

        argument += f'{python_to_go(args[key], arg_type)}'
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

def generate_go_tests(testcases: str, func_name: str, arg_types: list, returns: list) -> str:
    output = []

    try:
        localdict = {}
        exec(testcases, globals(), localdict)
        extracted_tcs = localdict["testcases"]
    except Exception as e:
        return output
    
    retVar = []
    for i in range(len(returns)):
        if returns[i] == "error":
            retVar.append(f"err")
        else:
            retVar.append(f"var{i}")

    for args, expected in extracted_tcs:
        tc = []
        tc.append(f"func Test{func_name[0].upper() + func_name[1:]}(t *testing.T) {{")
        arguments = create_arguments(args, arg_types)
        # print(arguments)
        func_call = ""
        if len(returns) > 0:
            ext_out = get_expected_value(expected, returns[0])
            func_call += f'\t{",".join(retVar)}'
            func_call += ' := '

        func_call += f'{func_name}{arguments}'
        tc.append(func_call)

        if len(returns) > 0:
            if isinstance(expected, Exception):
                tc.append(f'\tassert.Error(t, err)')
            elif "error" in returns:
                tc.append(f'\tassert.NoError(t, err, "should be %v", {ext_out})')

            if ext_out == "nil":
                tc.append('\tassert.Nil(t, var0)')
            elif "errors" in ext_out:
                tc.append(f'\texpectedErr := {ext_out}')
                tc.append(f'\tscore := fuzzy.PartialRatio(expectedErr.Error(), err.Error())')
                tc.append('\tif score < 60 {')
                tc.append(f'\t\tt.Fatalf("got Error %v, should be %v", err.Error(), expectedErr.Error())')
                tc.append('\t}')
            elif "*" in returns[0]:
                tc.append(f'\texpected := {ext_out}')
                tc.append(f'\tassert.Equal(t, &expected, var0)')
            elif "string" in returns[0]:
                tc.append(f'\tscore := fuzzy.PartialRatio({ext_out}, var0)')
                tc.append('\tif score < 60 {')
                tc.append(f'\t\tt.Fatalf("got %v, should be %v", var0, {ext_out})')
                tc.append('\t}')
            else:
                tc.append(f'\texpected := {ext_out}')
                tc.append(f'\tassert.Equal(t, expected, var0)')
            # else:
            #     if not isinstance(expected, Exception):
            #         tc.append(f"""score := fuzzy.PartialRatio({ext_out}, var0)""")
            #         # tc.append(f'\tassert.Equal(t, {ext_out}, var0)\n')
            #         tc.append(f'\tassert.Equal(t, {ext_out}, var0)\n')
        
        tc.append("}\n")

        output.append("\n".join(tc))

    return output

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

def extract_arg_types(code: str, func_name: str):
    """
    Extract argument types for a given Go function name from Go code.
    Handles grouped argument types like: func foo(a, b string, c int).
    """
    # Regex to capture the argument list of the specific function
    func_pattern = re.compile(rf"func\s*(?:\([^)]*\)\s*)?{func_name}\s*\(([^)]*)\)")
    match = func_pattern.search(code)
    if not match:
        return []
    
    args_str = match.group(1).strip()
    if not args_str:
        return []
    
    arg_types = []
    # Split arguments by commas, but handle grouped names with a type at the end
    parts = [p.strip() for p in args_str.split(",") if p.strip()]
    
    grouped = []
    for part in parts:
        tokens = part.split()
        if len(tokens) == 1:
            # just a name, type might come from grouping
            grouped.append(tokens[0])
        else:
            # names + type (possibly multiple names before type)
            names = tokens[:-1]
            typ = tokens[-1]
            if grouped:
                # previous grouped names also share this type
                arg_types.extend([typ] * len(grouped))
                grouped = []
            arg_types.extend([typ] * len(names))
    
    return arg_types

def extract_return_types(code, function_name) -> list:
    pattern = rf'func(?:\s*\([^)]*\))?\s*{re.escape(function_name)}\s*\([^)]*\)\s*(?P<ret>\([^)]+\)|[^\s{{]+)?\s*\{{'
    match = re.search(pattern, code)
    if not match:
        return []

    ret = match.group("ret")
    if not ret:
        return []

    return parseRetToList(ret.strip())

def parseRetToList(ret: str) -> list:
    if ret.startswith("(") and ret.endswith(")"):
        ret = ret[1:-1]
    parts = [r.strip().split() for r in ret.split(",") if r.strip()]
    return [p[-1] for p in parts]

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def clean_go_package_declaration(go_code: str) -> str:
    """
    Removes any 'package <name>' declaration from Go code
    and ensures exactly one 'package main' at the top.
    """
    lines = go_code.splitlines()

    # Remove all lines starting with 'package ' (any package name)
    filtered_lines = [
        line for line in lines
        if not re.match(r'^\s*package\s+\w+', line)
    ]

    # Prepend a single 'package main'
    cleaned_code = ["package main"] + filtered_lines

    # Remove possible leading empty lines after reinsertion
    while len(cleaned_code) > 1 and cleaned_code[1].strip() == "":
        cleaned_code.pop(1)

    return "\n".join(cleaned_code)
# main()