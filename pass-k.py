import os
import subprocess
import math
import glob
from pathlib import Path
import re

def run_unittest_on_file(sol_dir, code_file, test_file):
    temp_dir = "eval"
    os.makedirs(temp_dir, exist_ok=True)
    
    combined_file = os.path.join(temp_dir, code_file)
    test_dir = os.path.join(temp_dir, sol_dir)
    Path(test_dir).mkdir(parents=True, exist_ok=True)

    with open(combined_file, "w") as out_f:
        # Write the solution code first
        with open(code_file, "r") as sol_f:
            out_f.write(sol_f.read())
            out_f.write("\n\n")
        # Append the test code
        with open(test_file, "r") as test_f:
            out_f.write(test_f.read())

    f = open(f"{test_dir}/result.txt", "a")
    result = subprocess.run(
        ["python3", combined_file],
        stdout=f,
        stderr=f,
    )

    return result.returncode == 0


def compute_pass_k(n, c, k):
    if c == 0:
        return 0
    if k > n:
        return 1.0
    return 1.0 - (math.comb(n-c,k)/math.comb(n,k))

def main(test_file, solutions_dir, k):
    solution_files = sorted(glob.glob(os.path.join(solutions_dir, "*.py")))
    solution_files = [f for f in solution_files if not os.path.basename(f).startswith("test")]

    print(f"Evaluating {len(solution_files)} solutions against {test_file}")
    num_correct = 0
    for sol_file in solution_files:
        success = run_unittest_on_file(solutions_dir, sol_file, test_file)
        if success:
            num_correct += 1

    n = len(solution_files)
    pass_k = compute_pass_k(n, num_correct, k)

    print(f"Correct solutions: {num_correct}/{n}")
    print(f"pass@{k} = {pass_k:.4f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", required=True, help="Path to the unit test file")
    parser.add_argument("--solutions", required=True, help="Directory containing solution files")
    parser.add_argument("-k", type=int, required=True, help="Value of k for pass@k")
    args = parser.parse_args()

    main(args.test, args.solutions, args.k)