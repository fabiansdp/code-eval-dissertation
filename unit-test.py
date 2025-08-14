import json

# Buat nambahin hasil prompt
# def main():
#     lines = []
#     with open("dataset/batch_output_setup.jsonl", "rb") as f:
#         lines = [line.rstrip() for line in f]

#     secf_dict = dict()
#     with open("dataset/seccode-filtered-go.jsonl", "rb") as secf:
#         for line in secf:
#             data = json.loads(line.rstrip())
#             secf_dict[data["id"]] = data

#     for line in lines:
#         data = json.loads(line)
#         setup = data["response"]["body"]["output"][1]["content"][0]["text"].replace("```go","")
#         setup = setup.replace("```","")
#         secf_dict[data["custom_id"]]["unittest"]["setup"] = setup

#     output = []
#     for x in secf_dict:
#         output.append(secf_dict[x])

#     with open("dataset/seccode-filtered-go-v2.jsonl", "w") as fp:
#         for item in output:
#             fp.write(json.dumps(item) + "\n")

def main():
    correct_dict = dict()
    with open("dataset/correct.jsonl", "rb") as f:
        for line in f:
            data = json.loads(line)
            correct_dict[data["id"]] = data

    secf_dict = dict()
    with open("dataset/seccode-filtered.jsonl", "rb") as secf:
        for line in secf:
            data = json.loads(line.rstrip())
            secf_dict[data["id"]] = data

    for id in secf_dict:
        if id in correct_dict and id in secf_dict:
            secf_dict[id]["unittest"]["testcases"] = correct_dict[id]["unittest"]["testcases"]

    with open("dataset/seccode-plus-filtered.jsonl", "w") as fp:
        for id in secf_dict:
            fp.write(json.dumps(secf_dict[id]) + "\n")

if __name__ == "__main__":
    main()