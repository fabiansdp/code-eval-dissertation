# python3 parse_codeql.py -s codeql-results/py-codellama-0.0.csv -o sec-results/py-codellama-0.0
# python3 parse_codeql.py -s codeql-results/py-codellama-0.4.csv -o sec-results/py-codellama-0.4
# python3 parse_codeql.py -s codeql-results/py-codellama-0.8.csv -o sec-results/py-codellama-0.8
# python3 parse_codeql.py -s codeql-results/py-codellama-1.0.csv -o sec-results/py-codellama-1.0 
# python3 parse_codeql.py -s codeql-results/py-llama3.1-0.0.csv -o sec-results/py-llama3.1-0.0 
# python3 parse_codeql.py -s codeql-results/py-llama3.1-0.4.csv -o sec-results/py-llama3.1-0.4 
# python3 parse_codeql.py -s codeql-results/py-llama3.1-0.8.csv -o sec-results/py-llama3.1-0.8 
# python3 parse_codeql.py -s codeql-results/py-llama3.1-1.0.csv -o sec-results/py-llama3.1-1.0 
# python3 parse_codeql.py -s codeql-results/py-deepseekcoder-0.0.csv -o sec-results/py-deepseekcoder-0.0 
# python3 parse_codeql.py -s codeql-results/py-deepseekcoder-0.4.csv -o sec-results/py-deepseekcoder-0.4 
# python3 parse_codeql.py -s codeql-results/py-deepseekcoder-0.8.csv -o sec-results/py-deepseekcoder-0.8 
# python3 parse_codeql.py -s codeql-results/py-deepseekcoder-1.0.csv -o sec-results/py-deepseekcoder-1.0 
# python3 parse_codeql.py -s codeql-results/py-ministral-0.0.csv -o sec-results/py-ministral-0.0 
# python3 parse_codeql.py -s codeql-results/py-ministral-0.4.csv -o sec-results/py-ministral-0.4 
# python3 parse_codeql.py -s codeql-results/py-ministral-0.8.csv -o sec-results/py-ministral-0.8 
# python3 parse_codeql.py -s codeql-results/py-ministral-1.0.csv -o sec-results/py-ministral-1.0 
# python3 parse_codeql.py -s codeql-results/py-qwen-0.0.csv -o sec-results/py-qwen-0.0 
# python3 parse_codeql.py -s codeql-results/py-qwen-0.4.csv -o sec-results/py-qwen-0.4 
# python3 parse_codeql.py -s codeql-results/py-qwen-0.8.csv -o sec-results/py-qwen-0.8 
# python3 parse_codeql.py -s codeql-results/py-qwen-1.0.csv -o sec-results/py-qwen-1.0 
# python3 codeql_evaluation.py -r results/go-codellama-0.0.jsonl -o go-codellama-0.0 -l go > eval-logs/go-codellama-0.0.txt
# python3 codeql_evaluation.py -r results/go-codellama-0.4.jsonl -o go-codellama-0.4 -l go > eval-logs/go-codellama-0.4.txt
# python3 codeql_evaluation.py -r results/go-codellama-0.8.jsonl -o go-codellama-0.8 -l go > eval-logs/go-codellama-0.8.txt
# python3 codeql_evaluation.py -r results/go-codellama-1.0.jsonl -o go-codellama-1.0 -l go > eval-logs/go-codellama-1.0.txt
# python3 codeql_evaluation.py -r results/go-llama3.1-0.0.jsonl -o go-llama3.1-0.0 -l go > eval-logs/go-llama3.1-0.0.txt
# python3 codeql_evaluation.py -r results/go-llama3.1-0.4.jsonl -o go-llama3.1-0.4 -l go > eval-logs/go-llama3.1-0.4.txt
# python3 codeql_evaluation.py -r results/go-llama3.1-0.8.jsonl -o go-llama3.1-0.8 -l go > eval-logs/go-llama3.1-0.8.txt
# python3 codeql_evaluation.py -r results/go-llama3.1-1.0.jsonl -o go-llama3.1-1.0 -l go > eval-logs/go-llama3.1-1.0.txt
# python3 codeql_evaluation.py -r results/go-deepseekcoder-0.0.jsonl -o go-deepseekcoder-0.0 -l go > eval-logs/go-deepseekcoder-0.0.txt
# python3 codeql_evaluation.py -r results/go-deepseekcoder-0.4.jsonl -o go-deepseekcoder-0.4 -l go > eval-logs/go-deepseekcoder-0.4.txt
# python3 codeql_evaluation.py -r results/go-deepseekcoder-0.8.jsonl -o go-deepseekcoder-0.8 -l go > eval-logs/go-deepseekcoder-0.8.txt
# python3 codeql_evaluation.py -r results/go-deepseekcoder-1.0.jsonl -o go-deepseekcoder-1.0 -l go > eval-logs/go-deepseekcoder-1.0.txt
# python3 codeql_evaluation.py -r results/py-ministral-0.0.jsonl -o py-ministral-0.0 > eval-logs/py-ministral-0.0.txt
# python3 codeql_evaluation.py -r results/go-ministral-0.0.jsonl -o go-ministral-0.0 -l go > eval-logs/go-ministral-0.0.txt
# python3 codeql_evaluation.py -r results/go-ministral-0.4.jsonl -o go-ministral-0.4 -l go > eval-logs/go-ministral-0.4.txt
# python3 codeql_evaluation.py -r results/go-ministral-0.8.jsonl -o go-ministral-0.8 -l go > eval-logs/go-ministral-0.8.txt
# python3 codeql_evaluation.py -r results/go-ministral-1.0-v2.jsonl -o go-ministral-1.0 -l go > eval-logs/go-ministral-1.0.txt
python3 codeql_evaluation.py -r results/py-deepseekcoder-0.0.jsonl -o py-deepseekcoder-0.0 > eval-logs/py-deepseekcoder-0.0.txt
# python3 codeql_evaluation.py -r results/go-qwen-0.0.jsonl -o go-qwen-0.0 -l go > eval-logs/go-qwen-0.0.txt
# python3 codeql_evaluation.py -r results/go-qwen-0.4.jsonl -o go-qwen-0.4 -l go > eval-logs/go-qwen-0.4.txt
# python3 codeql_evaluation.py -r results/go-qwen-0.8.jsonl -o go-qwen-0.8 -l go > eval-logs/go-qwen-0.8.txt
# python3 codeql_evaluation.py -r results/go-qwen-1.0.jsonl -o go-qwen-1.0 -l go > eval-logs/go-qwen-1.0.txt