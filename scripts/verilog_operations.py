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
    nesting_level = 0
    current_always_block = []

    for line_number, line in enumerate(lines, start=1):
        # Check for assign statements.
        if line.strip().startswith('assign'):
            assign_statements[line_number] = line.strip()
            continue

        # Check for start of always block.
        if 'always' in line:
            inside_always = True
            current_always_block.append(line.strip())
            always_start = line_number
            continue

        # If inside always block, process the line.
        if inside_always:
            current_always_block.append(line.strip())
            if 'begin' in line:
                nesting_level += 1
            if 'end' in line:
                if nesting_level > 0:
                    nesting_level -= 1
                else:
                    # End of always block.
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
    assign_statements, always_blocks = extract_assign_and_always_blocks(
        lines)

    # print_assign_and_always_blocks(assign_statements, always_blocks)
    return assign_statements, always_blocks


def reconstruct_verilog_file(file_path, init_index, original_code, updated_code, upd_index):
    file_name = file_path.split('/')[-1]
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
        file_content = file_content.replace(original_code, updated_code, 1)
        f.write(file_content)
    f.close()
    print("[ SUCCESS ]")
