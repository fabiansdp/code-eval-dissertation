from pathlib import Path
import json
import re
from collections import Counter

def load_data(filename: str) -> list:
    data_arr = []
    with open(filename, encoding="utf8") as file:
        for line in file:
            data = json.loads(line)
            data_arr.append(data)

    return data_arr

# Define categorization function for invalid code subcategories
def categorize_invalid_code(result: str) -> str:
    r = result.lower()

    if "syntax error" in r:
        return "Syntax Error"
    if "undefined:" in r:
        return "Undefined Identifier"
    if "cannot assign" in r:
        return "Assignment Error"
    if "mismatched types" in r or "type mismatch" in r:
        return "Type Error"
    if "expected" in r and "found" in r:
        return "Parsing Error"
    if "multiple-value" in r and "in single-value" in r:
        return "Value Arity Error"

    # Default fallback for build/setup failed cases
    if "[build failed]" in r or "[setup failed]" in r:
        return "Build/Setup Failed"

    return "Other"


# Define main categorization function
def categorize_result(result: str) -> str:
    if not result:
        return "Others"

    r = result.lower()

    # 1. Timed Out
    if "timed out" in r or "context deadline exceeded" in r:
        return "Timed Out"

    # 2. Unexpected result
    if re.search(r"got[\s\S]*should be", r, re.IGNORECASE) or "not equal:" in r or "received unexpected error:" in r:
        return "Unexpected Result"

    # 3. Coding errors (runtime panic)
    if "panic:" in r or "fatal error: stack overflow" in r or "sync: unlock of unlocked mutex" in r or "error compiling regex:" in r or "error parsing" in r or "failed to parse" in r:
        return "Coding Errors"

    # 4. Invalid code (build/setup failed)
    if "[build failed]" in r or "[setup failed]" in r or "syntax error" in r or "undefined:" in r:
        print(r.encode("utf-8"))
        return "Invalid Code"

    # 5. External package errors (missing module/package)
    if "no required module provides package" in r or "pigar" in r or "pandoc" in r:
        return "External Package Errors"

    # 6. Others
    return "Others"

directory = Path('eval-go/new')
result_dict = dict()
other_arr = []
for file in directory.iterdir():  
    data_arr = load_data(file)
    err_dict = {
        "Timed Out": 0,
        "Unexpected Result": 0,
        "Invalid Code": 0,
        "Coding Errors": 0,
        "External Package Errors": 0,
        "Others": 0,
        "total_tests": 0
    }

    invalid_dict = {
        "Syntax Error": 0,
        "Undefined Identifier": 0,
        "Assignment Error": 0,
        "Type Error": 0,
        "Parsing Error": 0,
        "Value Arity Error": 0,
        "Build/Setup Failed": 0,
        "Other": 0
    }
    total_tests = 0
    for data in data_arr:
        for sample in data["results"]:
            for tc in sample:
                if tc["result"] == "passed":
                    continue

                total_tests += 1
                category = categorize_result(tc["result"])
                if category == "Invalid Code":
                    invalid_type = categorize_invalid_code(tc["result"])
                    invalid_dict[invalid_type] += 1
                
                if category == "Others":
                    other_arr.append(tc["result"])

                err_dict[category] += 1
        
        err_dict["total_tests"] = total_tests
        result_dict[file.stem] = {
            "errors": err_dict,
            "invalid_code_types": invalid_dict,
        }

# with open("summarized_err_go.json", "w") as f:
#     f.write(json.dumps(result_dict, indent=4))
# for result in other_arr:
#     try:
#         print(result)
#     except:
#         print(result.encode("utf-8"))