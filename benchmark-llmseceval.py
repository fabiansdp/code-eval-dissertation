import json
import csv
from ollama import generate

def construct_prompt(prompt):
    return f"""{prompt}

Return your answer in the form of code and comments only which can be easily copied into a Go file.
    """

language_set = set()
with open("dataset/llmseceval.csv") as csvfile:
    csvfile = csv.reader(csvfile)
    i = 0
    for row in csvfile:
        if i == 0:
            i += 1
            continue

        prompt = row[11].replace("<language>", "Go")
        response = generate(model='gemma3:1b', prompt=construct_prompt(prompt))
        s = response.response.replace("```go", "")
        s = s.replace("```", "")
        f = open( f'go-llmseceval/{row[0]}.go', 'w' )
        f.write(s)

        i += 1
        if i == 5:
            break