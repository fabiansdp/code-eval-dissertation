from typing import Iterable, Dict
import json
import re
import ast
import gzip
import os

def read_problems(evalset_file: str) -> Dict[str, Dict]:
    return {task["task_id"]: task for task in stream_jsonl(evalset_file)}


def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    if filename.endswith(".gz"):
        with open(filename, "rb") as gzfp:
            with gzip.open(gzfp, 'rt') as fp:
                for line in fp:
                    if any(not x.isspace() for x in line):
                        yield json.loads(line)
    else:
        with open(filename, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)


def write_jsonl(filename: str, data: Iterable[Dict], append: bool = False):
    """
    Writes an iterable of dictionaries to jsonl
    """
    if append:
        mode = 'ab'
    else:
        mode = 'wb'
    filename = os.path.expanduser(filename)
    if filename.endswith(".gz"):
        with open(filename, mode) as fp:
            with gzip.GzipFile(fileobj=fp, mode='wb') as gzfp:
                for x in data:
                    gzfp.write((json.dumps(x) + "\n").encode('utf-8'))
    else:
        with open(filename, mode) as fp:
            for x in data:
                fp.write((json.dumps(x) + "\n").encode('utf-8'))

def extract_first_code_block(text):
    # Match the first ```python ... ``` block
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    match2 = re.search(r"```go\n(.*?)\n```", text, re.DOTALL)
    match3 = re.search(r"```\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    
    if match2:
        return match2.group(1)
    
    if match3:
        return match3.group(1)
    
    return text

def extract_testcases_value(text):
    # Use regex to extract the full assignment to `testcases = {...}`
    match = re.search(r"testcases\s*=\s*({.*})", text, re.DOTALL)
    if match:
        return match.group(1)
        # try:
        #     return ast.literal_eval(dict_str)
        # except Exception as e:
        #     print("Error parsing testcases:", e)
        #     return None
    return text

def remove_markdown(output: str) -> str:
    return extract_first_code_block(output)

def read_testcase(filename: str):
    output = dict()
    for x in stream_jsonl(filename):
        item = {
            "CWE": x["CWE_ID"],
            "tc": x["unittest"]["testcases"],
            "setup": x["unittest"]["setup"],
            "function_name": x["task_description"]["function_name"]
        }

        output[x["id"]] = item

    return output

def read_results(filename: str):
    output = dict()
    for x in stream_jsonl(filename):
        codes = []
        for item in x["samples"]:
            codes.append(remove_markdown(item["text"]))
        output[x["id"]] = codes

    return output

