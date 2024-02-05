# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

# TODOs
# 1. Update system INSTRUCTIONS to standardize model responses.

import os
import re
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

PROMPT = (
    'I am preparing an exam. Please, add ONE bug in the provided Verilog code so students ' +
    'can find it during the exam. Make the bug a typical human engineering error:\n'
)

INSTRUCTIONS = (
    'You are a helpful assistant. ' +
    'If provided with a block of code always return the updated version of it.'
)


def parse_response(response):
    # Regex to extract a code block enclosed in triple backticks (```).
    matches = re.findall(r'```(?:\w+\s+)?(.*?)```', response, re.DOTALL)
    if matches:
        extracted_code_block = matches[0]
        return extracted_code_block
    else:
        return "No code block found."


def request_bug(code_block):
    prompt = PROMPT + '"\n' + code_block + '\n"'
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": prompt,
            }

        ],
        model="gpt-3.5-turbo",
    )
    response = completion.choices[0].message.content
    bug_description, updated_code_block = response, parse_response(response)
    return bug_description, updated_code_block
