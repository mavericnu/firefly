# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import json
import subprocess
import multiprocessing
from verilog_operations import parse_verilog_file


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
    with open("buffer.json", "w") as outfile:
        json.dump(verilog_buffer, outfile)
