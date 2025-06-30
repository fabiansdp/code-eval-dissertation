from datasets import load_dataset

ds = load_dataset("Virtue-AI-HUB/SecCodePLT")
ds["insecure_coding"].to_json("dataset/seccode.json")
# ds = load_dataset("s2e-lab/SecurityEval")
# print(ds["train"].to_csv("dataset/seceval.csv"))

# specific language (e.g. Python) 
# dataset = load_dataset("Fsoft-AIC/the-vault-function", split_set=["train"], languages=['rust'], trust_remote_code=True)
# dataset["train"].to_csv("dataset/the-vault-rust")