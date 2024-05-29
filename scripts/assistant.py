# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import json
from openai import OpenAI

INSTRUCTIONS = '''You are a part of a mutation testing system for hardware designs written in Verilog. Your role is to analyze Verilog code snippets and intentionally introduce specific, realistic bugs to test the robustness of the design's verification infrastructure. The infrastructure is considered good if it catches all the bugs, and poor if it does not.

Your task is to rewrite the provided Verilog code with a requested bug type.

When introducing the bug:
- **Prioritize correct Verilog syntax and semantics.** The bug should be subtle and realistic.
- **Consider the context of the provided code snippet.** A bug must be relevant within the larger module.

Return the result exclusively in JSON format, with the following requirements:
- The JSON must contain exactly two properties: 'explanation' and 'code'.
- 'explanation' and 'code' must be strings.
- 'explanation' must contain your step-by-step thought process for introducing each bug.
- 'code' must contain the updated buggy code. It must be consistent with the module context. There is no need to add comments.

Example JSON response:
```json
{
    "explanation": "To introduce a stuck-at zero fault in the provided ALU module, I will choose a line of code that has a significant effect on the calculation or functionality and modify it so that a particular part of the calculation or operation is permanently stuck at zero. Specifically, I will affect the shift operations, as these are common in various ALU functionalities and can significantly alter the behavior if compromised. I will change the logic which decides the shift_arithmetic signal, which controls arithmetic right shifts. Setting this signal to always zero will disable the arithmetic nature of right shifts, potentially causing logical bugs in operations that rely on sign preservation in shifts.",
    "code": "shift_arithmetic = 1'b0;"
}
```

IMPORTANT:
- The JSON response must not include dictionaries, lists, or any non-string data types for the 'explanation' and 'code' values.
- The code must remain synthesizable after the addition of a bug. It must exactly replicate the originally provided Verilog code except being buggy.

'''

api_key, assistant_id = os.getenv("OPENAI_API_KEY"), os.getenv("ASSISTANT_ID")
if not api_key or not assistant_id:
    raise ValueError("Environment variables not set")

client = OpenAI(api_key=api_key)

assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)

# This variable should be updated to select other modules
module = open("cv32e40p_int_controller.sv", "r").read()
context = f"Hardware module for context:\n```Verilog\n{module}\n```"
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    instructions=INSTRUCTIONS + context
)


thread = client.beta.threads.create()

bug_type = "stuck-at-0"

with open("cv32e40p_int_controller.sv", "r") as file:
    lines = file.readlines()

for i in range(len(lines) - 4):
    snippet = "".join(lines[i:i+5])

    content = f"Bug type: {bug_type}\nCode:\n```Verilog\n{snippet}\n```"
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    if run.status == 'completed':
        responses = client.beta.threads.messages.list(thread_id=thread.id)
        for response in responses.data:
            if response.role != "user":
                response_content = response.content[0].text.value
                try:
                    response_json = json.loads(response_content)
                    print("Assistant Response (JSON):",
                          json.dumps(response_json, indent=4))
                except json.JSONDecodeError:
                    print("Failed to parse JSON response")
    else:
        print(f"Run status: {run.status}")

    if i == 0:
        break


client.beta.threads.delete(thread_id=thread.id)


def main():
    with open("cv32e40p_int_controller.sv", "r") as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        line.strip()
        if line.startswith("//") or line == "\n":
            continue
        if "//" in line:
            half = line.split("//")[0].strip()
            new_lines.append(half)
            continue
        new_lines.append(line)

    for line in new_lines:
        print(line)


if __name__ == "__main__":
    main()
