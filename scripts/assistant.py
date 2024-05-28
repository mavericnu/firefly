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

thread = client.beta.threads.create()

thread = client.beta.threads.create(
    instructions="Focus on providing detailed support for software installation issues."
)


message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=""
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


# updated_instructions = "New instructions for the assistant."
# updated_assistant = client.beta.assistants.update(
#     assistant_id=assistant_id,
#     instructions=updated_instructions
# )
# print(f"Updated Instructions: {updated_assisstant.instructions}")

# client.beta.threads.end(thread_id=thread.id)