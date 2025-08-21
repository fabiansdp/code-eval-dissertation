from data import read_results, read_testcase
from pathlib import Path
import subprocess
from ctx import create_tempdir
from gotester import cd
import argparse

def evaluate_security(sample_file: str, out_file: str, language: str = "python"):
    tcs = read_testcase("dataset/seccode-go-plus-filtered.jsonl")
    samples = read_results(sample_file)
    # idx = 0
    with create_tempdir():
        file_dir = f"codeql"
        Path(file_dir).mkdir(parents=True, exist_ok=True)
        for task_id in tcs:
            function_name = tcs[task_id]["function_name"]
            results = samples[task_id]

            for i in range(len(results)):
                if f"{function_name}" not in results[i]:
                    print("Mismatched function name: ", function_name)
                    continue

                setup = ""
                # if tcs[task_id]["setup"] not in results[i]:
                #     setup = tcs[task_id]["setup"] + "\n\n"
                if "package main" not in results[i]:
                            setup = tcs[task_id]["setup"] + "\n\n"

                with open(f"{file_dir}/{task_id}-{i}.go", "w") as file:
                    file.write(f"""{setup}
{results[i]}""")

        with cd(f"{file_dir}"):
            subprocess.run(f"codeql database create db --language={language} --overwrite", shell=True)        
            # subprocess.run(f"codeql database analyze db -v --format=sarif-latest --output=/app/codeql-results/{out_file}.sarif", shell=True)        
            subprocess.run(f"codeql database analyze db -v --format=csv --output=/app/codeql-results/{out_file}.csv", shell=True)        


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-r", "--results", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-l", "--language", type=str, default="python")

def main():
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    args = parser.parse_args()
    evaluate_security(sample_file=args.results, out_file=args.output, language=args.language)

if __name__ == "__main__":
    main()