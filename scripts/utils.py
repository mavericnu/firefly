# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import os
import json
import subprocess
from verilog_operations import parse_verilog_file


def replace_file(file_path):
    fp_splitted = file_path.split('/')
    cmd1 = ['mv', file_path, '../original-files/']
    cmd2 = ['mv', fp_splitted[-1], '/'.join(fp_splitted[:-1])]
    subprocess.run(cmd1)
    subprocess.run(cmd2)


def parse_dir(directory):
    results = dict()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".v") or file.endswith(".sv"):
                file_path = os.path.join(root, file)
                # print(f"Processing file: {file_path}")
                assign_statements, always_blocks = parse_verilog_file(file_path)
                results[file_path] = {
                    "assign_statements": assign_statements,
                    "always_blocks": always_blocks
                }
    return results


def export_to_json(dictionary):
    with open("buffer.json", "w") as outfile:
        json.dump(dictionary, outfile)
