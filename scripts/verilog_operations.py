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
            if inside_always:
                current_always_block.append(line)
            continue

        if inside_block_comment:
            if inside_always:
                current_always_block.append(line)
            continue

        line_stripped = line.strip()
        if line_stripped.startswith('//'):
            if inside_always:
                current_always_block.append(line)
            continue

        if line_stripped.startswith('assign'):
            assign_statements[line_number] = line.rstrip()
            continue

        if 'always' in line_stripped or inside_always:
            if 'always' in line_stripped:
                inside_always = True
                always_start = line_number
                current_always_block = [line.rstrip()]
            elif inside_always:
                current_always_block.append(line.rstrip())
                if '{' in line or 'begin' in line_stripped:
                    nesting_level += 1
                if '}' in line or 'end' in line_stripped:
                    nesting_level -= 1
                    if nesting_level <= 0:
                        inside_always = False
                        always_blocks[always_start] = '\n'.join(current_always_block)
                        current_always_block = []
                        nesting_level = 0
        elif not inside_always:
            pass

    return assign_statements, always_blocks


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
