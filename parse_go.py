import json
import re

def snake_to_camel(snake_str):
    """Convert snake_case string to camelCase."""
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def parse_and_convert_vars(docstring):
    """Extract variable names and convert them to camelCase."""
    # Match lines like "- var_name: type, description"
    pattern = r'([a-zA-Z_]+)'
    matches = re.findall(pattern, docstring)

    output = docstring
    for var in matches:
        camel = snake_to_camel(var)
        output = output.replace(var, camel)
    
    return output

def main():
    lines = []
    with open("dataset/seccode-filtered-go.jsonl", "rb") as file:
        for line in file:
            lines.append(line)

    output = []
    for line in lines:
        data = json.loads(line)
        temp_name = data["task_description"]["function_name"]
        new_name = snake_to_camel(data["task_description"]["function_name"])
        data["task_description"]["function_name"] = new_name
        data["task_description"]["description"] = data["task_description"]["description"].replace("Python", "Go")
        data["task_description"]["description"] = data["task_description"]["description"].replace(temp_name, new_name)

        # data["task_description"]["arguments"] = parse_and_convert_vars(data["task_description"]["arguments"])
        # data["task_description"]["context"] = parse_and_convert_vars(data["task_description"]["context"])
        data["task_description"]["return"] = parse_and_convert_vars(data["task_description"]["return"])
        data["ground_truth"] = None

        output.append(data)

    with open("dataset/seccode-filtered-go.jsonl", "w") as f:
        for item in output:
            f.write(json.dumps(item) + "\n")


if __name__ == "__main__":
    main()