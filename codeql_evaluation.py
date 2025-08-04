from data import read_results, read_testcase
from pathlib import Path
import subprocess
from ctx import create_tempdir, reliability_guard, swallow_io, time_limit, TimeoutException
from gotester import cd

def main():
    tcs = read_testcase("dataset/seccode-filtered.jsonl")
    samples = read_results("results/py-qwen.jsonl")
    # idx = 0
    with create_tempdir():
        for task_id in tcs:
            function_name = tcs[task_id]["function_name"]
            result = samples[task_id]
            if f"def {function_name}" not in result:
                print("Mismatched function name: ", function_name)
                # print("Salah goblok nama fungsinya")
                # print(function_name)
                # print(result)
                continue

            setup = ""
            if tcs[task_id]["setup"] not in result:
                setup = tcs[task_id]["setup"] + "\n\n"

            file_dir = f"codeql"
            Path(file_dir).mkdir(parents=True, exist_ok=True)
            with open(f"{file_dir}/{task_id}.py", "w") as file:
                file.write(f"""{setup}
    {result}
    """)

        with cd(f"{file_dir}"):
            subprocess.run(f"codeql database create db --language=python --overwrite", shell=True)        
            subprocess.run(f"codeql database analyze db --format=csv --output=/app/codeql-results/qwen.csv", shell=True)        

if __name__ == "__main__":
    main()