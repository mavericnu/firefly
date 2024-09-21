# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import anthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)

print(message.content)

def hello_world():
    print("Hello, World!")