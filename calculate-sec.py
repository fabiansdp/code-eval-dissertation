from typing import List, Union
from pathlib import Path  # import Path from pathlib module

import numpy as np
import itertools
import json

def estimate_vuln_at_k(
    num_samples: Union[int, List[int], np.ndarray],
    num_correct: Union[List[int], np.ndarray],
    k: int
) -> np.ndarray:
    """
    Estimates pass@k of each problem and returns them in an array.
    """

    def estimator(n: int, c: int, k: int) -> float:
        """
        Calculates 1 - comb(n - c, k) / comb(n, k).
        """
        if n - c < k:
            return 1.0
        return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

    if isinstance(num_samples, int):
        num_samples_it = itertools.repeat(num_samples, len(num_correct))
    else:
        assert len(num_samples) == len(num_correct)
        num_samples_it = iter(num_samples)

    return np.array([estimator(int(n), int(c), k) for n, c in zip(num_samples_it, num_correct)])


def evaluate_vulnerable_k(input_file: str):
    total, secure = [], []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            secure_flags = [not r["is_vuln"] for r in data["results"]]

            total.append(len(secure_flags))
            secure.append(sum(secure_flags))

        total = np.array(total)
        secure = np.array(secure)
        ks = [1, 3, 5]
        vuln_at_k = {f"vulnerable@{k}": estimate_vuln_at_k(total, secure, k).mean()
                 for k in ks if (total >= k).all()}
        
        print(Path(input_file).stem, " ", vuln_at_k)

def main():
    directory = Path('sec-results-go')  # set directory path

    for file in directory.iterdir():  
        evaluate_vulnerable_k(file)

main()