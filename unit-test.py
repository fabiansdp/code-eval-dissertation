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
    lines = []
    with open("dataset/batch_go_test.jsonl", "rb") as f:
        lines = [line.rstrip() for line in f]

    secf_dict = dict()
    output_tc = []
    with open("dataset/seccode-go-filtered-v2.jsonl", "rb") as secf:
        for line in secf:
            data = json.loads(line.rstrip())
            if data["unittest"]["testcases"] == "":
                secf_dict[data["id"]] = data
            else:
                output_tc.append(data)

    for line in lines:
        data = json.loads(line)
        setup = data["response"]["body"]["output"][1]["content"][0]["text"].replace("```go","")
        setup = setup.replace("```","")
        if data["custom_id"] in secf_dict:
            secf_dict[data["custom_id"]]["unittest"]["setup"] = setup

    output_gpt = []
    for x in secf_dict:
        output_gpt.append(secf_dict[x])

    with open("dataset/seccode-go-gpt.jsonl", "w") as fp:
        for item in output_gpt:
            fp.write(json.dumps(item) + "\n")

    with open("dataset/seccode-go-tc.jsonl", "w") as fp:
        for item in output_tc:
            fp.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    main()