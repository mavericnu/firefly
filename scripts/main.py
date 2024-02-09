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

    lines[init_index + upd_index] = lines[init_index +
                                          upd_index].replace(original_code, updated_code)
    f = open(file_name, 'w')
    f.writelines(lines)
    f.close()


def main():
    assign_statements, always_blocks = parse_verilog([file_path])

    test_assign = list(assign_statements.items())[0]
    original_code, updated_code, line_number, bug_description = request_bug(
        test_assign[1])

    reconstruct_verilog(
        test_assign[0] - 1, original_code, updated_code, line_number - 1)

    # test_always = list(always_blocks.items())[0]


main()
