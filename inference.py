import json
import argparse
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from tqdm import tqdm
from tqdm.auto import trange
# from huggingface_hub import login
# login()

def tokenize_inputs(tokenizer, prompt):
    tokenized_prompt = tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)

    return tokenized_prompt

def generate_prompt(llm, params, prompt):
     return llm.generate(prompt, params)

def setup_args(parser):
    parser.add_argument("-m", "--model")
    parser.add_argument("-s", "--source")
    parser.add_argument("-dm", "--dirmodel", default="/cs/student/projects2/sec/2024/fpranoto/models")
    parser.add_argument("-o", "--output")

def main():
    parser = argparse.ArgumentParser()
    setup_args(parser)
    args = parser.parse_args()

    model_name = args.model
    output_dir = args.output
    source_dataset = args.source

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    llm = LLM(
        model=model_name, 
        download_dir=args.dirmodel,
        trust_remote_code=True,
        gpu_memory_utilization=1
        # max_model_len=32096
    )
    
    inputs = []
    with open(source_dataset, "r") as file:
        for line in file:
            data = json.loads(line.rstrip())
            inputs.append({
                "id": data["id"],
                # "tokenized_prompt": tokenize_inputs(tokenizer, data["prompt"]) + "<think></think>"
                "tokenized_prompt": tokenize_inputs(tokenizer, data["prompt"])
            })

    # for temp in [0.0,0.2,0.4,0.6,0.8,1.0]:
    for temp in [0.8,1.0]:
        results = []
        for x in tqdm(inputs):
            llm_outputs = []
            for i in trange(10):
                sampling_params = SamplingParams(temperature=temp, max_tokens=1000)
                try:
                    output = llm.generate(x["tokenized_prompt"], sampling_params, use_tqdm=False)
                    llm_outputs.append({
                        "index": i,
                        "text": output[0].outputs[0].text
                    })
                except Exception as e:
                    print(x["id"], e)
                
            results.append({
                "id": x["id"],
                "samples": llm_outputs
            })

        with open(f"{output_dir}-{temp}.jsonl", "w") as fp:
            for item in results:
                fp.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    main()
