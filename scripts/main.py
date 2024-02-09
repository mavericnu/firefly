# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

# TODOs:
# 1. Как хэндлить большие VS маленькие файлы
# 2. Как менеджить старые-новые копии.

# Notes:
# Промпт резалт ломается, когда посылаемый-возвращаемый код длинный
# Возможное решение: просить сокращенный original_code & updated_code
# Сплитнуть оба стринга по '\n' и менять 1-by-1.
#   Если останутся строчки кода в updated_code, аппенднуть под конец.

import sys

from prompt_chatgpt import request_bug
from breakdown_verilog import parse_verilog

file_path = sys.argv[1]
file_name = file_path.split('/')[-1]


def reconstruct_verilog(init_index, original_code, updated_code, upd_index):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    updated_code_lines = updated_code.split('\n')
    n = len(updated_code_lines)

    if n == 1:
        if lines[init_index + upd_index].find(original_code) != -1:
            print("[ REPLACEMENT SUCCESSFUL ]\n")
        else:
            print("[ REPLACEMENT UNSUCCESSFUL]\n")
            print("Searching for: ", original_code)
            print("Real line: ", lines[init_index + upd_index])
            return
        lines[init_index + upd_index] = lines[init_index +
                                              upd_index].replace(original_code, updated_code)
    # else:

    f = open(file_name, 'w')
    f.writelines(lines)
    f.close()


def main():
    assign_statements, always_blocks = parse_verilog([file_path])

    # print(assign_statements.keys())

    # test_assign = list(assign_statements.items())[2]
    # original_code, updated_code, line_number, bug_description = request_bug(
    #     test_assign[1])

    # reconstruct_verilog(
    #     test_assign[0] - 1, original_code, updated_code, line_number - 1)

    print(always_blocks.keys())
    print()

    test_always = list(always_blocks.items())[4]
    original_code, updated_code, line_number, bug_description = request_bug(
        test_always[1])

    reconstruct_verilog(
        test_always[0] - 1, original_code, updated_code, line_number - 1)

    print("ORIGINAL CODE:")
    print(original_code)
    print()
    print("UPDATED CODE:")
    print(updated_code)
    print()
    print("BUG DESCRIPTION:")
    print(bug_description)


main()
