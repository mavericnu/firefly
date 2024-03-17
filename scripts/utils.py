# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import json
import subprocess
import multiprocessing
from verilog_operations import parse_verilog_file
from prompt_gpt import request_bug


def replace_file(file_path):
    directory, filename = os.path.split(file_path)
    subprocess.run(['mv', file_path, '../original-files/'])
    subprocess.run(['mv', filename, directory])


def parse_dir(directory):
    results = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".v") or file.endswith(".sv"):
                file_path = os.path.join(root, file)
                assign_statements, always_blocks = parse_verilog_file(
                    file_path)
                results[file_path] = {
                    "assign_statements": assign_statements,
                    "always_blocks": always_blocks
                }
    return results


def create_verilog_buffer(directory):
    verilog_buffer = parse_dir(directory)
    with open("../buffers/buffer.json", "w") as outfile:
        json.dump(verilog_buffer, outfile)


def insert_bug(code):
    original_snippet, buggy_snippet = request_bug(code)
    if isinstance(original_snippet, str) and isinstance(buggy_snippet, str):
        modified_code = code.replace(original_snippet, buggy_snippet)
        return modified_code
    else:
        print("ERROR")
        print(f"Original snippet:\n{original_snippet}")
        print(f"Buggy snippet:\n{buggy_snippet}")
        return code


def modify_json_values(data):
    if isinstance(data, dict):
        return {k: modify_json_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [modify_json_values(v) for v in data]
    elif isinstance(data, str):
        return insert_bug(data)
    else:
        return data


def create_buggy_buffer(input_filename):
    with open(input_filename, 'r') as infile:
        data = json.load(infile)
    modified_data = modify_json_values(data)
    with open("../buffers/bugs.json", 'w') as outfile:
        json.dump(modified_data, outfile, indent=4)
