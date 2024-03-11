# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import sys
from prompt_chatgpt import request_bug
from breakdown_verilog import parse_verilog
from utils import *


def main():
    # file_path = sys.argv[1]

    # assign_statements, always_blocks = parse_verilog(file_path)

    # i = 1

    # test_assign = list(assign_statements.items())[i]
    # original_code, updated_code, line_number, bug_description = request_bug(
    #     test_assign[1])

    # reconstruct_verilog(file_path, test_assign[0] - 1,
    #                     original_code, updated_code, line_number - 1)

    # print()
    # print(
    #     f"[ Check from line {list(assign_statements.keys())[i]} and further ]\n")

    # test_always = list(always_blocks.items())[i]
    # original_code, updated_code, line_number, bug_description = request_bug(
    #     test_always[1])

    # reconstruct_verilog(file_path, test_always[0] - 1,
    #                     original_code, updated_code, line_number - 1)

    # print()
    # print(f"[ Check from line {list(always_blocks.keys())[i]} and further ]\n")

    # print("ORIGINAL CODE:")
    # print(original_code)
    # print()
    # print("UPDATED CODE:")
    # print(updated_code)
    # print()
    # print("BUG DESCRIPTION:")
    # print(bug_description)

    # replace_file(file_path)

    directory_path = "/home/maveric/workspace/cva6/core"
    verilog_buffer = parse_dir(directory_path)
    export_to_json(verilog_buffer)


main()
