# Copyright (c) 2025 Maveric @ NU and Texer.ai. All rights reserved.
import json
import os
import subprocess

from pathlib import Path


def read_file(file_path, read_mode="r"):
    with open(file_path, "r") as f:
        if read_mode == "r":
            return f.read()
        elif read_mode == "rl":
            return f.readlines()


def read_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_results_directory():
    results_path = Path("results")
    if results_path.exists():
        print(f"-- Results directory already exists at '{results_path.absolute()}'.")
        return

    results_path.mkdir(parents=True, exist_ok=True)
    print(f"-- Results directory created at '{results_path.absolute()}'.")


def spawn_design_copy(design_root_path):
    sim_dir = "./sim"
    cmd = f"cp -r {design_root_path} {sim_dir}/"
    subprocess.run(cmd, shell=True, executable="/bin/bash")
    return f"{sim_dir}/{design_root_path.split('/')[-1]}"


def spawn_design_copies(design_root_path, num_jobs):
    sim_dir = "./sim"
    design_copies = []
    for i in range(num_jobs):
        job_dir = os.path.join(sim_dir, f"job_{i}")
        if not os.path.exists(job_dir):
            os.makedirs(job_dir)
        cmd = f"cp -r {design_root_path}/* {job_dir}/"
        subprocess.run(cmd, shell=True, executable="/bin/bash")
        design_copies.append(job_dir)
    return design_copies


def _write_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def _apply_mutation(target_file, mutation_data):
    original_content = read_file(target_file)
    modified_content = original_content.replace(
        mutation_data["original_code"], mutation_data["mutated_code"]
    )
    _write_file(target_file, modified_content)


def _execute_simulation(design_copy_path):
    cmd = f"cd {design_copy_path} && source execute-tests.sh"
    subprocess.run(
        cmd, shell=True, capture_output=True, executable="/bin/bash", text=True
    )


def _collect_simulation_results(design_copy_path, results_dir):
    output_file = os.path.join(design_copy_path, "execute-tests-output.txt")
    if os.path.exists(output_file):
        subprocess.run(
            f"cp {output_file} {results_dir}/", shell=True, executable="/bin/bash"
        )
    log_files_path = os.path.join(
        design_copy_path, "verif/sim/out_*/veri-testharness_sim/*"
    )
    subprocess.run(
        f"cp {log_files_path} {results_dir}/ 2>/dev/null || true",
        shell=True,
        executable="/bin/bash",
    )


def _clean_simulation_artifacts(design_copy_path):
    output_file = os.path.join(design_copy_path, "execute-tests-output.txt")
    subprocess.run(f"rm {output_file}", shell=True, executable="/bin/bash")

    sim_dir = f"{design_copy_path}/verif/sim"
    subprocess.run(
        f"cd {sim_dir} && make clean_all", shell=True, executable="/bin/bash"
    )
    subprocess.run(
        f"cd {sim_dir} && rm logfile.log", shell=True, executable="/bin/bash"
    )
    subprocess.run(f"cd {sim_dir} && rm -rf out_*", shell=True, executable="/bin/bash")


def run_simulation(design_copy_path, mutation):
    design_copy_path = os.path.abspath(design_copy_path)
    file_path, mutation_data = mutation
    target_file = f"{design_copy_path}/{file_path.split('/cva6/')[-1]}"

    unique_id = f"{os.path.basename(file_path)}_{mutation_data['mutation_type']}_{hash(mutation_data['original_code'])}"
    results_dir = os.path.join("results", unique_id)
    results_dir = os.path.abspath(results_dir)
    os.makedirs(results_dir, exist_ok=True)

    original_content = read_file(target_file)
    _apply_mutation(target_file, mutation_data)

    print(f"-- Running simulation in {design_copy_path} with mutation in {target_file}")
    _execute_simulation(design_copy_path)
    _collect_simulation_results(design_copy_path, results_dir)
    _clean_simulation_artifacts(design_copy_path)
    _write_file(target_file, original_content)
    return {unique_id: {"target_file": os.path.basename(file_path)} | mutation_data}


def run_simulations():
    create_results_directory()

    config = read_json("config.json")
    design_root_path = config["design_root_path"]
    # cmd = config["cmd"]
    # sim_path = config["sim_path"]
    # num_jobs = int(config["num_jobs"])

    mutations = read_json("mutations.json")
    mutation_tuples = []
    for target_file, target_mutations in mutations.items():
        for target_mutation in target_mutations:
            mutation_tuples.append((target_file, target_mutation))

    total_mutations = len(mutation_tuples)

    # Create design copies for parallel execution
    design_copy_path = spawn_design_copy(design_root_path)

    print(f"-- Starting simulations for {total_mutations} mutations sequentially...")

    # Execute simulations iteratively
    results = {}
    completed_count = 0
    failed_count = 0

    for mutation in mutation_tuples:
        try:
            result = run_simulation(design_copy_path, mutation)
            results.update(result)
            completed_count += 1
            print(
                f"-- Progress: {completed_count}/{total_mutations} simulations completed."
            )

            # Dump intermediate results every 5 mutations
            if completed_count % 5 == 0:
                ids_file_path = os.path.join("results", "ids.json")
                with open(ids_file_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4)
                print(
                    f"-- Intermediate results saved to '{ids_file_path}' after {completed_count} mutations"
                )
        except Exception as e:
            failed_count += 1
            print(f"-- Simulation task failed: {e}")

    print(
        f"-- Completed {completed_count} successful simulations out of {total_mutations} total mutations attempted."
    )
    if failed_count > 0:
        print(f"-- {failed_count} simulations failed.")

    ids_file_path = os.path.join("results", "ids.json")
    with open(ids_file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"-- Unique IDs saved to '{ids_file_path}'")
    return True
