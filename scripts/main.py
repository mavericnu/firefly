# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

# TODOs:
# 1. Handle large files. (?)

import sys
import subprocess

from prompt_chatgpt import request_bug
from breakdown_verilog import parse_verilog

file_path = sys.argv[1]
file_name = file_path.split('/')[-1]


def reconstruct_verilog(init_index, original_code, updated_code, upd_index):
    f = open(file_name, 'w')
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines
        index = init_index + upd_index
        if lines[index].find(original_code) == -1:
            print(
                "[ Replacement using lines is unsuccessful. Trying another method... ]")
            # print("Looked for: ", original_code)
            # print("Found: ", lines[index])
            raise Exception('')
        lines[index] = lines[index].replace(original_code, updated_code)
        f.writelines(lines)
    except:
        with open(file_path, 'r') as file:
            file_content = file.read()
        if file_content.find(original_code) == -1:
            print("[ Replacement using the whole file is also unsuccessful ]")
            f.close()
            return
        file_content = file_content.replace(original_code, updated_code)
        f.write(file_content)
    f.close()
    print("[ SUCCESS ]")


def replace_file(file):
    cmd1 = ['mv', '../uart-verilog/' + file, '../original-files/']
    cmd2 = ['mv', file, '../uart-verilog/']
    subprocess.run(cmd1)
    subprocess.run(cmd2)


def main():
    assign_statements, always_blocks = parse_verilog([file_path])

    i = 0

    test_assign = list(assign_statements.items())[i]
    original_code, updated_code, line_number, bug_description = request_bug(
        test_assign[1])

    reconstruct_verilog(
        test_assign[0] - 1, original_code, updated_code, line_number - 1)

    print()
    print(f"[ Check from line {list(assign_statements.keys())[i]} and further ]\n")

    # test_always = list(always_blocks.items())[i]
    # original_code, updated_code, line_number, bug_description = request_bug(
    #     test_always[1])

    # reconstruct_verilog(test_always[0] - 1,
    #                     original_code, updated_code, line_number - 1)

    # print()
    # print(f"[ Check from line {list(always_blocks.keys())[i]} and further ]\n")

    print("ORIGINAL CODE:")
    print(original_code)
    print()
    print("UPDATED CODE:")
    print(updated_code)
    print()
    print("BUG DESCRIPTION:")
    print(bug_description)

    replace_file(file_name)


main()
