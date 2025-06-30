import json

with open("dataset/seccode.json") as file:
    lines = [line.rstrip() for line in file]

changed_data = []
for line in lines:
    data = json.loads(line)
    data["task_description"]["description"] = data["task_description"]["description"].replace("Python", "Go")
    changed_data.append(data)

with open(f'dataset/go-seccode.json', 'w', encoding='utf-8') as f:
    json.dump(changed_data, f, ensure_ascii=False, indent=4)
# language_set = set()
# inst_list = list()

# for item in data:
#     language_set.add(item["language"])
#     if item["language"] == "go":
#         inst_list.append(item)

# with open('dataset/instruct-go.json', 'w', encoding='utf-8') as f:
#     json.dump(inst_list, f, ensure_ascii=False, indent=4)

# print(language_set)