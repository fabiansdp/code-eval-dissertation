import json
import random
import string

class JsonlFileOperator:
    def __init__(self, model_name, messages, filename='output.jsonl', max_tokens=1000):
        self.model_name = model_name
        self.messages = messages
        self.filename = filename
        self.max_tokens = max_tokens
        self.message_list = self.create_message_list()

    @staticmethod
    def generate_random_id(prefix="request", length=6, fixed_id=None):
        if fixed_id:
            return fixed_id

        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return f"{prefix}-{random_id}"

    def create_message_list(self):
        message_list = []
        for i in range(len(self.messages)):
            message_list.append({
                "custom_id": self.messages[i]["id"], 
                "method": "POST", 
                "url": "/v1/responses", 
                "body": {
                    "model": self.model_name, 
                    "input": self.messages[i]["input"]
                }
            })

        return message_list

    def write_jsonl_file(self):
        with open(self.filename, 'w') as f:
            for item in self.message_list:
                f.write(json.dumps(item) + "\n")

    @staticmethod
    def jsonl_to_dict(jsonl_string):
        dict_list = []
        for line in jsonl_string.strip().split("\n"):
            if line.strip():
                dict_list.append(json.loads(line))

        return dict_list