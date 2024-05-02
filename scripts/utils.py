# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed

from verilog_operations import parse_verilog_file
from prompt_gpt import request_bug


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
    with open("../bp_buffers/bp_common/buffer.json", "w") as outfile:
        json.dump(verilog_buffer, outfile)


def insert_bug(code):
    original_snippet, buggy_snippet = request_bug(code)
    if isinstance(original_snippet, str) and isinstance(buggy_snippet, str):
        modified_code = code.replace(original_snippet, buggy_snippet)
        return modified_code
    else:
        print("ERROR")
        # print(f"Original snippet:\n{original_snippet}")
        # print(f"Buggy snippet:\n{buggy_snippet}")
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
    with open("../bp_buffers/bp_me/bugs.json", 'w') as outfile:
        json.dump(modified_data, outfile, indent=4)


def load_json_from_file(filepath):
    with open(filepath, "r") as file:
        return json.load(file)


def compare_json_leaves(path, json1, json2):
    if isinstance(json1, dict) and isinstance(json2, dict):
        keys1, keys2 = set(json1.keys()), set(json2.keys())
        common_keys = keys1 & keys2

        for key in common_keys:
            yield from compare_json_leaves(os.path.join(path, key), json1[key], json2[key])
        for key in keys1 - keys2:
            yield (os.path.join(path, key), json1[key], None)
        for key in keys2 - keys1:
            yield (os.path.join(path, key), None, json2[key])
    else:
        yield (path, json1, json2)


def get_code_blocks(json1, json2):
    return list(compare_json_leaves("", json1, json2))


def complete_task_in_parallel(func, code_blocks, max_workers=4):
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_code_block = {
            executor.submit(func, code_block): code_block for code_block in code_blocks
        }

        for future in as_completed(future_to_code_block):
            code_block = future_to_code_block[future]
            try:
                future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (code_block, exc))
