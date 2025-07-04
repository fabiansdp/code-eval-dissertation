from jsonl import JsonlFileOperator
import json

def setup_prompt(setup):
    return f"""{setup}

Given this setup code in Python, transform it to be compatible with Go function.

Output the code in a markdown code block, i.e., between triple backticks (```) with the language specified as Go.
    """

def unittest_prompt(data):
    return f"""Function Name: {data["task_description"]["function_name"]}

Description: {data["task_description"]["description"]}

Context (global variables and imported packages): {data["task_description"]["context"]}

Arguments: {data["task_description"]["arguments"]}

Return: {data["task_description"]["return"]}

Raise: {data["task_description"]["raise"]}

Security policy: {data["task_description"]["security_policy"]}

Setup Code:
```go
{data["unittest"]["setup"]}
```

Please create unit tests according to these specifications, Output the code in a markdown code block, i.e., between triple backticks (```) with the language specified as Go.
    """

# def main():
#     model_name = "o3-mini"

#     lines = []
#     with open("dataset/seccode-filtered-go.jsonl") as file:
#         lines = [line.rstrip() for line in file]

#     messages = []
#     for line in lines:
#         data = json.loads(line)
#         messages.append({
#             "id": data["id"],
#             "input": setup_prompt(data["unittest"]["setup"])
#         })

#     operator = JsonlFileOperator(model_name, messages, filename="setup-go.jsonl")
#     operator.write_jsonl_file()

def main():
    model_name = "o3-mini"

    lines = []
    with open("dataset/seccode-filtered-go-v2.jsonl") as file:
        lines = [line.rstrip() for line in file]

    messages = []
    for line in lines:
        data = json.loads(line)
        if data["unittest"]["testcases"] == "":
            messages.append({
                "id": data["id"],
                "input": unittest_prompt(data)
            })

    operator = JsonlFileOperator(model_name, messages, filename="unittest-go.jsonl")
    operator.write_jsonl_file()

if __name__ == "__main__":
    main()