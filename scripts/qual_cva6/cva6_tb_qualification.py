import os
import sys
import subprocess
from uuid import uuid4

from utils import load_json_from_file, get_code_blocks, complete_task_in_parallel

CVA6_SOURCE_FILES = [
    "riscv_pkg.sv", "dm_pkg.sv", "ariane_pkg.sv", "std_cache_pkg.sv", "alu.sv",
    "ariane.sv", "branch_unit.sv", "cache_ctrl.sv", "commit_stage.sv", "compressed_decoder.sv",
    "controller.sv", "csr_buffer.sv", "csr_regfile.sv", "decoder.sv", "ex_stage.sv", "btb.sv",
    "bht.sv", "ras.sv", "instr_scan.sv", "frontend.sv", "id_stage.sv", "scoreboard.sv",
    "store_buffer.sv", "store_unit.sv", "tlb.sv", "cva6_tlb_sv32.sv", "acc_dispatcher.sv",
    "dm_csrs.sv", "dm_mem.sv", "dm_top.sv", "dmi_cdc.sv", "dmi_jtag.sv", "dmi_jtag_tap.sv",
    "apb_timer.sv", "timer.sv", "issue_read_operands.sv", "issue_stage.sv", "lfsr.sv",
    "load_unit.sv", "load_store_unit.sv", "miss_handler.sv", "mmu.sv", "cva6_mmu_sv32.sv",
    "mult.sv", "std_cache_subsystem.sv", "perf_counters.sv", "ptw.sv", "cva6_ptw_sv32.sv",
    "instruction_tracer_if.sv", "instruction_tracer_pkg.sv", "instr_realigner.sv", "vdregs.sv",
    "pcgen_stage.sv", "re_name.sv", "icache.sv", "nbdcache.sv", "sram_wrapper.sv"
]


def cva6_copy_dir(source, destination):
    dir_id = str(uuid4())
    source_dir = os.path.basename(source)
    dest_dir = os.path.join(destination, "testing", dir_id, source_dir)

    os.makedirs(dest_dir, exist_ok=True)
    subprocess.run(["cp", "-r", source, dest_dir])

    target_dir = dest_dir + "cva6"
    return dir_id, target_dir


def cva6_filter(tuples):
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

    subprocess.run(f"source {script}", shell=True,
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


def main():
    json_data1 = load_json_from_file("/home/maveric/workspace/firefly/buffers/buffer.json")
    json_data2 = load_json_from_file("/home/maveric/workspace/firefly/buffers/bugs.json")

    code_blocks = sorted(cva6_filter(get_code_blocks(json_data1, json_data2)), key=lambda x: x[0])

    complete_task_in_parallel(func=cva6_qualification, code_blocks=code_blocks)


if __name__ == "__main__":
    main()
