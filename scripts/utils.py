# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import subprocess


def reconstruct_verilog(file_path, init_index, original_code, updated_code, upd_index):
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


def replace_file(file_path):
    fp_splitted = file_path.split('/')
    cmd1 = ['mv', file_path, '../original-files/']
    cmd2 = ['mv', fp_splitted[-1], '/'.join(fp_splitted[:-1])]
    subprocess.run(cmd1)
    subprocess.run(cmd2)
