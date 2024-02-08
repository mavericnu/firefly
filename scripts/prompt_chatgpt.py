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
    original_code, updated_code, line, description = r["original_code"], r[
        "updated_code"], r["line_number"], r["description"]
    return original_code, updated_code, line, description


def request_bug(code_block):
    instruction = INSTRUCTIONS['assistant_experimental']
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
    original_code, updated_code, line_number, bug_description = parse_response(
        response)
    return original_code, updated_code, line_number, bug_description
