from typing import Iterable, Dict
import json
import re
import ast

def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    with open(filename, "r") as fp:
        for line in fp:
            if any(not x.isspace() for x in line):
                yield json.loads(line)

def extract_first_code_block(text):
    # Match the first ```python ... ``` block
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    match2 = re.search(r"```\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    
    if match2:
        return match2.group(1)
    
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
        output[x["id"]] = remove_markdown(x["generated_text"])

    return output


# # Construct the check program and run it.
# for task_id in tcs:
#     if task_id not in results:
#         continue

    # Construct the check program and run it.
    
#     print(check_program)
#     exec(check_program)
# check_program = (
#         results[task_id]
#         + "\n\n"
#         + tcs[task_id]["setup"]
#         + "\n\n"
#         + tcs[task_id]["tc"]
#         + "\n"
#         + """
# tcs = []
# for tc in testcases['capability']:
#     tcs.append({
#     "kwargs": tc[0],
#     "output": tc[1]
#     })
# """ 
#         +
# f"""
# for item in tcs:
#     output = {tcs[task_id]["function_name"]}(**item["kwargs"])
#     assert output == item["output"]
# """
#     )  
