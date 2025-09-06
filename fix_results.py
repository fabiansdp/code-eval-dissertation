import ast
import json
from pathlib import Path  # import Path from pathlib module


def parse_no_results(file_path):
    results = {}

    with open(file_path, "r") as f:
        for line in f:
            if line.startswith("No results key:"):
                # Strip prefix
                content = line.split("No results key:")[1].strip()
                
                # The line ends with task_id repeated, so split by double spaces
                # Example: "{'task_id': '7c6aab34', ...}   7c6aab34"
                parts = content.rsplit("}", 1)
                if len(parts) >= 2:
                    json_part = parts[0] + "}"
                    task_id = parts[1].strip()
                    
                    # Convert the dict-like string into a real Python dict
                    try:
                        parsed_dict = ast.literal_eval(json_part)
                        if task_id in results:
                            results[task_id].append(parsed_dict)
                        else:
                            results[task_id] = [parsed_dict]
                    except Exception as e:
                        print(f"Failed to parse line: {line}\nError: {e}")

    return results


def load_data(filename: str) -> list:
    data_arr = []
    with open(filename, encoding="utf8") as file:
        for line in file:
            data = json.loads(line)
            data_arr.append(data)

    return data_arr

num_tcs = dict()
with open("summarized.json") as jf:
    data = json.load(jf)
    for task_id in data["py-codellama-0.0"]["task_stats"]:
        num_tcs[task_id] = data["py-codellama-0.0"]["task_stats"][task_id]["total_tests"] / 10

directory = Path('eval-go')
for file in directory.iterdir():  
    if file.is_file() and file.suffix == ".txt":  # Check if it's a file
        print(file)
        failures = parse_no_results(file)
        result_arr = []
        with open(f"eval-go/{file.stem}.jsonl", encoding="utf8") as fp:
            for line in fp:
                data = json.loads(line)
                if data["task_id"] in failures:
                    for failure in failures[data["task_id"]]:
                        temp_id = failure["task_id"]
                        total_tests = 0
                        if temp_id in num_tcs:
                            total_tests = int(num_tcs[temp_id])
                        data["statistics"].insert(failure["completion_id"], {
                            "total_tests": total_tests,
                            "passed_tests": 0,
                            "success_rate": 0.0
                        })
                result_arr.append(data)

        with open(f"eval-go/new/{file.stem}.jsonl", "wb") as fp:
            for x in result_arr:
                fp.write((json.dumps(x) + "\n").encode('utf-8'))