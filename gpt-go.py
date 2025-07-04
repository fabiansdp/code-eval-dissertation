from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def main():
    # Load the model and tokenizer
    client = OpenAI()

    batch_input_file = client.files.create(
        file=open("unittest-go.jsonl", "rb"),
        purpose="batch"
    )

    resp = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={
            "description": "Creating seccode go unit tests"
        }
    )
    print(resp)


if __name__ == "__main__":
    main()