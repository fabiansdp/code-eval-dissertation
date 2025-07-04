import json

with open("dataset/seccode-py.json") as file:
    data = json.load(file)
    index = 0
    for item in data:
        f = open( f'seccode/py/test/{index}-{item["task_description"]["function_name"]}.py', 'w', encoding="utf-8")
        s = item["unittest"]["testcases"].replace("```python", "")
        s = s.replace("```", "")
        f.write(s)
        index+=1

# print(lines[0])
# changed_data = []
# for line in lines:
#     data = json.loads(line)
#     data["task_description"]["description"] = data["task_description"]["description"].replace("Python", "Go")
#     changed_data.append(data)

# with open(f'dataset/go-seccode.json', 'w', encoding='utf-8') as f:
#     json.dump(changed_data, f, ensure_ascii=False, indent=4)
# language_set = set()
# inst_list = list()

# for item in data:
#     language_set.add(item["language"])
#     if item["language"] == "go":
#         inst_list.append(item)

# with open('dataset/instruct-go.json', 'w', encoding='utf-8') as f:
#     json.dump(inst_list, f, ensure_ascii=False, indent=4)

# print(language_set)