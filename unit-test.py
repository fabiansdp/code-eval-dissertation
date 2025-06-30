import json
from ollama import generate
from pathlib import Path

def construct_prompt(row, setup):
    return f"""Function Name: {row["function_name"]}

Prompt for code generation: {row["description"]}

Context (global variables and imported packages): {row["context"]}

Arguments: {row["arguments"]}

Return: {row["return"]}

Raise: {row["raise"]}

Security policy: {row["security_policy"]}

Setup Code:
```python
{setup["setup"]}
```

The function has already been implemented, but please create unit tests according to these specifications, Output the code in a markdown code block, i.e., between triple backticks (```) with the language specified as Python. No need to create the {row["function_name"]} function, just the unit tests.
    """

with open("dataset/seccode.json") as file:
    lines = [line.rstrip() for line in file]

idx = 0
for line in lines:
    data = json.loads(line)
    Path(f'seccode/py/{data["task_description"]["function_name"]}').mkdir(parents=True, exist_ok=True)

    prompt = construct_prompt(data["task_description"], data["unittest"]) 
    response = generate(model='gemma3:1b', prompt=prompt)
    s = response.response.replace("```python", "")
    s = s.replace("```", "")
    f = open( f'seccode/py/{data["task_description"]["function_name"]}/test.py', 'w' )
    f.write(s)
    break