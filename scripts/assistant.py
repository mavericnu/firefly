# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

assistant_id = os.getenv("ASSISTANT_ID")
if not assistant_id:
    raise ValueError("ASSISTANT_ID environment variable not set")


client = OpenAI(api_key=api_key)

assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)


# This variable should be updated to select other modules
module = open("cv32e40p_int_controller.sv", "r").read()
instructions = f"Hardware module for context:\n```Verilog\n{module}\n```"
thread = client.beta.threads.create(
    instructions=instructions
)

bug_type = "stuck-at-0"


# This variable should be dynamically updated to select different code snippets
code_snippet = ""
content = f"Bug type: {bug_type}\nCode:\n```Verilog\n{code_snippet}\n```"
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
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print(messages)
else:
    print(run.status)


client.beta.threads.end(thread_id=thread.id)
