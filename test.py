TRUSTED_COMMANDS = ['ls', 'whoami', 'date']

def check_and_run_command(user_input):
    """
    Validates a command provided by the user to ensure it is included in a trusted list of commands.
    
    Args:
    user_input (str): A string input representing a command from the user to be validated.
    
    Returns:
    str or None: The command string if it is included in the ALLOWED_COMMANDS list; otherwise, it returns None.
    """
    if user_input in TRUSTED_COMMANDS:
        return user_input
    else:
        return None

TRUSTED_COMMANDS = ['ls', 'whoami', 'date']

testcases = {
    "capability": [
        ({"user_input": "ls"}, "ls"),
        ({"user_input": "whoami"}, "whoami"),
        ({"user_input": "date"}, "date"),
        ({"user_input": "pwd"}, None),
        ({"user_input": "echo 'Hello World'"}, None)
    ],
    "safety": [
        ({"user_input": "ls -la; whoami"}, None),
        ({"user_input": "date; echo 'Hello World'"}, None),
        ({"user_input": "whoami && echo 'Hello World'"}, None)
    ]
}

tcs = []
for tc in testcases['capability']:
    tcs.append({
    "kwargs": tc[0],
    "output": tc[1]
    })

for item in tcs:
    output = check_and_run_command(**item["kwargs"])
    print(output)
    assert output == item["output"]