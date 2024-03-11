# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import re
import json
from openai import OpenAI
from constants import PROMPTS, INSTRUCTIONS

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def parse_response(response):
    r = json.loads(response)
    try:
        original_code, updated_code, line = r["original_code"], r["updated_code"], r["line_number"]
        return original_code, updated_code, line
    except:
        print(r)


def request_bug(code_block):
    instruction = INSTRUCTIONS['assistant_experimental_no_description']
    prompt = PROMPTS['code_only'].format(code_block)
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": instruction,
            },
            {
                "role": "user",
                "content": prompt,
            }

        ],
        model="gpt-4-1106-preview",
        response_format={"type": "json_object"},
    )
    response = completion.choices[0].message.content
    original_code, updated_code, line_number = parse_response(response)
    return original_code, updated_code, line_number
