import csv
import json
import argparse

from pathlib import Path

def extract_vulnerable_samples(csv_file: str, output: str):
    vuln_entries = dict()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue  # skip malformed rows

            rule_name = row[0].strip()
            rule_desc = row[1].strip()
            filepath = row[4]  # column with "/<taskid>-<sampleid>.py"
            filename = Path(filepath).name  # e.g., "5cf42722-3.py"

            if filename.endswith(".go") and "-" in filename:
                task_id, sample_id = filename[:-3].rsplit("-", 1)
                if task_id not in vuln_entries:
                    vuln_entries[task_id] = {
                        int(sample_id): {
                            "rule_name": rule_name,
                            "rule_desc": rule_desc
                        }
                    }
                else:
                    vuln_entries[task_id][int(sample_id)] = {
                            "rule_name": rule_name,
                            "rule_desc": rule_desc
                        }

    result_dict = dict()
    with open("eval-data/py-codellama-0.0.jsonl", "r") as fp:
        for line in fp:
            data = json.loads(line)
            result_dict[data["task_id"]] = {
                "results": []
            }

            if data["task_id"] not in vuln_entries:
                result_dict[data["task_id"]]["results"] = [{
                    "is_vuln": False,
                    "rule_name": "",
                    "rule_desc": ""
                } for i in range(len(data["results"]))]
                continue

            for i in range(len(data["results"])):
                if i in vuln_entries[data["task_id"]]:
                    result_dict[data["task_id"]]["results"].append({
                        "is_vuln": True,
                        "rule_name": vuln_entries[data["task_id"]][i]["rule_name"],
                        "rule_desc": vuln_entries[data["task_id"]][i]["rule_desc"]
                    })
                else:
                    result_dict[data["task_id"]]["results"].append({
                        "is_vuln": False,
                        "rule_name": "",
                        "rule_desc": ""
                    })

    with open(f"{output}.jsonl", "w") as fp:
        for id in result_dict:
            fp.write(json.dumps(result_dict[id]) + "\n")


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-s", "--source", type=str)
    parser.add_argument("-o", "--output", type=str)

def main():
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    args = parser.parse_args()
    extract_vulnerable_samples(args.source, args.output)


# Example usage
if __name__ == "__main__":
    main()