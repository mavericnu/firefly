from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import sys
import subprocess
import json
from uuid import uuid4

import random

from constants import CVA6_SOURCE_FILES


def cva6_copy_dir(source, destination):
    dir_id = str(uuid4())
    source_dir = os.path.basename(source)
    dest_dir = os.path.join(destination, "testing", dir_id, source_dir)

    os.makedirs(dest_dir, exist_ok=True)
    subprocess.run(["cp", "-r", source, dest_dir])

    target_dir = dest_dir + "cva6"
    return dir_id, target_dir


def load_json_from_file(filepath):
    with open(filepath, "r") as file:
        return json.load(file)


def compare_json_leaves(path, json1, json2):
    if isinstance(json1, dict) and isinstance(json2, dict):
        keys1, keys2 = set(json1.keys()), set(json2.keys())
        common_keys = keys1 & keys2

        for key in common_keys:
            yield from compare_json_leaves(os.path.join(path, key), json1[key], json2[key])
        for key in keys1 - keys2:
            yield (os.path.join(path, key), json1[key], None)
        for key in keys2 - keys1:
            yield (os.path.join(path, key), None, json2[key])
    else:
        yield (path, json1, json2)


def get_code_blocks(json1, json2):
    return list(compare_json_leaves("", json1, json2))


def filter(tuples):
    base_filter_result = [
        tpl for tpl in tuples
        if tpl[2] != None and "cva6/tools" not in tpl[0]
    ]
    filter_result = [
        tpl for tpl in base_filter_result
        if any(
            part for part in tpl[0].split("/")
            if ".sv" in part and part in CVA6_SOURCE_FILES
        )
    ]
    return filter_result


def cva6_add_bug(tpl):
    root_copy = "/home/maveric/cva6_env/copies/cva6/"
    dest_path = "/home/maveric/cva6_env/copies/"

    path, original, modified = tpl
    start = path.find("cva6/") + 5
    end = path.find(".sv") + 3 if ".sv" in path else path.find(".v") + 2
    location = path[start:end]
    dir_id, curr_dir = cva6_copy_dir(source=root_copy, destination=dest_path)
    target_file = os.path.join(curr_dir, location)

    with open(target_file, "r") as infile:
        content = infile.read()

    if original in content:
        updated_content = content.replace(original, modified)
    else:
        print("[ Not found ]")
        subprocess.run(
            f"cd ../../ && rm -rf {dir_id}", shell=True, executable="/bin/bash", cwd=curr_dir)
        sys.exit()

    with open(target_file, "w") as outfile:
        outfile.write(updated_content)

    return dir_id, target_file, curr_dir


def cva6_qualification(code_block):
    dir_id, trgt, tmp = cva6_add_bug(code_block)
    script = tmp + "/run_tests.sh"

    result = subprocess.run(f"source {script}", shell=True,
                            executable="/bin/bash", cwd=tmp)

    file = tmp + "/output.txt"
    with open(file, "r") as infile:
        content = infile.read()

    if "error" in content.lower():
        print('\n===================================START===================================')
        print(f"Detected bug in: {trgt}")
        print(f"ORIG:\n{code_block[1]}\n")
        print(f"MOD:\n{code_block[2]}")
        print('====================================END====================================\n')
    else:
        print('\n===================================START===================================')
        print(f"NOT detected bug in: {trgt}")
        print(f"ORIG:\n{code_block[1]}\n")
        print(f"MOD:\n{code_block[2]}")
        print('====================================END====================================\n')

    subprocess.run(f"mkdir ../../../logs/{dir_id} && mv verif/sim/out_*/veri-testharness_sim ../../../logs/{dir_id}/",
                   shell=True, executable="/bin/bash", cwd=tmp)
    subprocess.run(f"mv output.txt {dir_id}.txt && mv {dir_id}.txt ../../../logs/{dir_id}/",
                   shell=True, executable="/bin/bash", cwd=tmp)
    subprocess.run(f"cd ../../ && rm -rf {dir_id}", shell=True, executable="/bin/bash", cwd=tmp)


def complete_task_in_parallel(code_blocks, max_workers=4):
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_code_block = {
            executor.submit(cva6_qualification, code_block): code_block for code_block in code_blocks
        }

        for future in as_completed(future_to_code_block):
            code_block = future_to_code_block[future]
            try:
                future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (code_block, exc))


def main():
    json_data1 = load_json_from_file("/home/maveric/workspace/firefly/buffers/buffer.json")
    json_data2 = load_json_from_file("/home/maveric/workspace/firefly/buffers/bugs.json")

    code_blocks = sorted(filter(get_code_blocks(json_data1, json_data2)), key=lambda x: x[0])

    complete_task_in_parallel(code_blocks[400:])


if __name__ == "__main__":
    main()
