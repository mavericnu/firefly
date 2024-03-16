# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

def read_verilog_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def extract_assign_and_always_blocks(lines):
    assign_statements = {}
    always_blocks = {}
    inside_always = False
    inside_block_comment = False
    nesting_level = 0
    current_always_block = []
    always_start = None

    for line_number, line in enumerate(lines, start=1):
        if '/*' in line:
            inside_block_comment = True
        if '*/' in line:
            inside_block_comment = False
            continue

        if inside_block_comment or line.strip().startswith('//'):
            continue

        stripped_line = line.strip()

        if stripped_line.startswith('assign') and not inside_block_comment:
            assign_statements[line_number] = stripped_line
            continue

        if 'always' in stripped_line and not inside_block_comment:
            inside_always = True
            always_start = line_number

        if inside_always:
            current_always_block.append(stripped_line)
            if 'begin' in stripped_line:
                nesting_level += 1
            elif 'end' in stripped_line:
                if nesting_level > 0:
                    nesting_level -= 1
                else:
                    inside_always = False
                    always_blocks[always_start] = '\n'.join(
                        current_always_block)
                    current_always_block = []

    return assign_statements, always_blocks


def print_assign_and_always_blocks(assign_statements, always_blocks):
    print("Assigns:")
    print("-----------------------------")
    for statement in assign_statements:
        print(statement)

    print("\nAlways blocks:")
    print("-----------------------------")
    for block in always_blocks:
        print(block)


def parse_verilog_file(file_path):
    lines = read_verilog_file(file_path)
    return extract_assign_and_always_blocks(lines)


def reconstruct_verilog_file(file_path, original_code, updated_code):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()

        if original_code in file_content:
            updated_file_content = file_content.replace(original_code, updated_code)

            with open(file_path, 'w') as file:
                file.write(updated_file_content)

            print("Replacement within a file is successful.")
        else:
            print("Error: Original code not found in the file.")
    except Exception as e:
        print(f"Error: An exception occurred. {e}")
