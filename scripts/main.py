# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import sys

from prompt_chatgpt import request_bug
from breakdown_verilog import parse_verilog

file_path = sys.argv[1]


def main():
    assign_statements, always_blocks = parse_verilog([file_path])
    original_code_block = always_blocks[3]
    updated_code_block, bug_description = request_bug(original_code_block)
    
    print("-------- ORIGINAL CODE: --------")
    print(original_code_block)
    print()
    print("-------- UPDATED CODE: --------")
    print(updated_code_block)
    print()
    print("-------- BUG DESCRIPTION: --------")
    print(bug_description)

main()
