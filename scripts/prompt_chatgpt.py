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
    code, description =  r["updated_code"], r["description"]
    return code, description 


def request_bug(code_block):
    instruction = INSTRUCTIONS['general']
    prompt = PROMPTS['detailed'].format(code_block)
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
    updated_code, bug_description = parse_response(response)
    return updated_code, bug_description
