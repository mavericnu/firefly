from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import sys
import subprocess
import json
from uuid import uuid4

import random

COMMANDS = [
    "bash ci/check_design.sh > output.txt 2>&1",
    "bash ci/lint.sh verilator > output.txt 2>&1",
    "bash ci/yosys.sh > output.txt 2>&1",
    # "bash ci/bloodgraph.sh > output.txt 2>&1",
    "bash ci/dcache_regress.sh verilator > output.txt 2>&1",
    "bash ci/icache_regress.sh verilator > output.txt 2>&1",
    "bash ci/me_regress.sh verilator > output.txt 2>&1", # TAKES TOO MUCH TIME
    "bash ci/single_core_atomics.sh verilator > output.txt 2>&1",
    "bash ci/single_core_testlist.sh verilator RISCV_TESTLIST > output.txt 2>&1",
    "bash ci/weird_config.sh verilator > output.txt 2>&1",
    "bash ci/check_loops.sh > output.txt 2>&1",
    "bash ci/l2e_config.sh verilator > output.txt 2>&1",
    "bash ci/surelog.sh > output.txt 2>&1",
    "bash ci/accelerator.sh verilator > output.txt 2>&1",
    "bash ci/checkpoint.sh verilator > output.txt 2>&1",
    "bash ci/single_core_testlist.sh verilator MISC_TESTLIST > output.txt 2>&1",
    "bash ci/single_core_testlist.sh verilator BEEBS_TESTLIST > output.txt 2>&1",
    "bash ci/single_core_testlist.sh verilator COREMARK_TESTLIST > output.txt 2>&1"
]


def bp_copy_dir(source, destination):
    dir_id = str(uuid4())
    dest_dir = os.path.join(destination, dir_id)

    os.makedirs(dest_dir, exist_ok=True)

    subprocess.run(f"cp -r {source}/* .", shell=True,
                   executable="/bin/bash", cwd=dest_dir)

    return dir_id, dest_dir


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
    result = [
        tpl for tpl in tuples
        if tpl[1].split() != tpl[2].split()
    ]
    return result


def bp_add_bug(tpl):
    init_copy = "/home/maveric/bp_env/black-parrot-sim/black-parrot"
    dest_path = "/home/maveric/bp_env/black-parrot-sim/"

    path, original, modified = tpl
    start = path.find("/black-parrot/") + 14
    end = path.find(".sv") + 3 if ".sv" in path else path.find(".v") + 2
    location = path[start:end]
    dir_id, curr_dir = bp_copy_dir(source=init_copy, destination=dest_path)
    target_file = os.path.join(curr_dir, location)

    with open(target_file, "r") as infile:
        content = infile.read()

    if original in content:
        updated_content = content.replace(original, modified)
    else:
        print("[ Not found ]")
        subprocess.run(f"cd ../ && rm -rf {dir_id}", shell=True, executable="/bin/bash", cwd=curr_dir)
        sys.exit()

    with open(target_file, "w") as outfile:
        outfile.write(updated_content)

    return dir_id, target_file, curr_dir


def bp_qualification(code_block):
    dir_id, trgt, instance_dir = bp_add_bug(code_block)
    
    subprocess.run(f"touch {dir_id}.txt",  shell=True, executable="/bin/bash", cwd=instance_dir)
    
    for command in COMMANDS:
        subprocess.run(f"export TOP=/home/maveric/bp_env/black-parrot-sim/{dir_id} && " + command, shell=True, executable="/bin/bash", cwd=instance_dir)
        subprocess.run(f"cat output.txt >> {dir_id}.txt", shell=True, executable="/bin/bash", cwd=instance_dir)

        file = instance_dir + "/output.txt"
        with open(file, "r") as infile:
            content = infile.read()

        if "FAILED" in content:
            print(f"\n==========START==========\nDetected bug in: {trgt}\nORIG:\n{code_block[1]}\n\nMOD:\n{code_block[2]}\n===========END===========\n")
            subprocess.run(f"mv {dir_id}.txt ../../logs/", shell=True, executable="/bin/bash", cwd=instance_dir)
            subprocess.run(f"cd ../ && rm -rf {dir_id}", shell=True, executable="/bin/bash", cwd=instance_dir)
            sys.exit()
        elif "PASSED" in content:
            continue
        else:
            print(f"\n==========START==========\nUnexpected output in: {trgt}\nORIG:\n{code_block[1]}\n\nMOD:\n{code_block[2]}\n===========END===========\n")
            continue
    
    print(f"\n==========START==========\nNOT detected bug in: {trgt}\nORIG:\n{code_block[1]}\n\nMOD:\n{code_block[2]}\n===========END===========\n")

    subprocess.run(f"mv {dir_id}.txt ../../logs/", shell=True, executable="/bin/bash", cwd=instance_dir)
    subprocess.run(f"cd ../ && rm -rf {dir_id}", shell=True, executable="/bin/bash", cwd=instance_dir)



def complete_task_in_parallel(code_blocks, max_workers=2):
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_code_block = {
            executor.submit(bp_qualification, code_block): code_block for code_block in code_blocks
        }

        for future in as_completed(future_to_code_block):
            code_block = future_to_code_block[future]
            try:
                future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (code_block, exc))


def main():
    flag = "top"
    json_data1 = load_json_from_file(f"/home/maveric/workspace/firefly/bp_buffers/bp_{flag}/buffer.json")
    json_data2 = load_json_from_file(f"/home/maveric/workspace/firefly/bp_buffers/bp_{flag}/bugs.json")

    code_blocks = sorted(filter(get_code_blocks(json_data1, json_data2)), key=lambda x: x[0])
    
    # print(len(code_blocks))
    
    # complete_task_in_parallel(code_blocks[:10])


if __name__ == "__main__":
    main()
