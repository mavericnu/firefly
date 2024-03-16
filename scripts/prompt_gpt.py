# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import re
import json
from openai import OpenAI
from constants import PROMPTS, INSTRUCTIONS


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=api_key)


def parse_response(response):
    try:
        r = json.loads(response)
        original_code = r["original_code"]
        updated_code = r["updated_code"]
        return original_code, updated_code
    except KeyError as e:
        print(f"KeyError: missing {e} in response")
        return None, None
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return None, None


def request_bug(code_block):
    instruction = INSTRUCTIONS['assistant_experimental_no_description']
    prompt = PROMPTS['code_only'].format(code_block)
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
        )
        response = completion.choices[0].message.content
        return parse_response(response)
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return None, None
