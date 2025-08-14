# python3 evaluation.py -tc dataset/seccode-go-tc.jsonl -r results/go-deepseekcoder-7b.jsonl -o eval/go-deepseekcoder.jsonl -l go > eval/go-deepseekcoder.txt
# python3 evaluation.py -tc dataset/seccode-plus-filtered.jsonl -r new-results/py-qwen-0.0.jsonl -o new-eval/py-qwen-0.0.jsonl > new-eval/py-qwen-0.0.txt
# python3 evaluation.py -tc dataset/seccode-plus-filtered.jsonl -r new-results/py-qwen-0.4.jsonl -o new-eval/py-qwen-0.4.jsonl > new-eval/py-qwen-0.4.txt
python3 evaluation.py -tc dataset/seccode-plus-filtered.jsonl -r new-results/py-qwen-0.8.jsonl -o new-eval/py-qwen-0.8.jsonl > new-eval/py-qwen-0.8.txt
python3 evaluation.py -tc dataset/seccode-plus-filtered.jsonl -r new-results/py-qwen-1.0.jsonl -o new-eval/py-qwen-1.0.jsonl > new-eval/py-qwen-1.0.txt
# python3 evaluation.py -tc dataset/correct.jsonl -r new-results/py-qwen-0.0.jsonl -o new-eval/py-qwen-0.0.jsonl > new-eval/py-qwen-0.0.txt
# python3 evaluation.py -tc dataset/correct.jsonl -r new-results/py-qwen-0.2.jsonl -o new-eval/py-qwen-0.2.jsonl > new-eval/py-qwen-0.2.txt