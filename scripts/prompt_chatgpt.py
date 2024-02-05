# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import re
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

PROMPT = (
    'I am creating an exam. Please, add one bug in the provided Verilog code ' +
    'so people can find it during the exam. Make the bug a typical human ' +
    'engineering error. Return an answer in JSON format. The first key must be ' +
    '"description" with an extensive description of the proposed bug. The second ' +
    'key must be "code" with the updated buggy code:\n'
)

INSTRUCTIONS = (
    '- Be highly organized;\n' +
    '- Be proactive and anticipate my needs;\n' +
    '- Mistakes erode my trust, so be accurate and thorough;\n' +
    '- If provided with a block of code always return the updated version of it.'
)


def parse_response(response):
    r = json.loads(response)
    description, code = r["description"], r["code"]
    return description, code


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
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
    )
    response = completion.choices[0].message.content
    bug_description, updated_code_block = parse_response(response)
    return bug_description, updated_code_block
