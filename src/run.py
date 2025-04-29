# Copyright (c) 2025 Maveric @ NU and Texer.ai. All rights reserved.
import json
import os
import subprocess

from pathlib import Path


# Define all functions.
def read_file(file_path, read_mode="r"):
    with open(file_path, "r") as f:
        return f.readlines() if read_mode == "rl" else f.read()


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
    sim_dir = Path("./sim")
    sim_dir.mkdir(parents=True, exist_ok=True)

    cmd = f"cp -r {design_root_path} {str(sim_dir)}/"
    subprocess.run(cmd, shell=True, executable="/bin/bash")

    copied_design_path = sim_dir / Path(design_root_path).name
    return str(copied_design_path)


def _write_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def _apply_mutation(target_file, mutation_data):
    original_content = read_file(target_file)
    modified_content = original_content.replace(
        mutation_data["original_code"], mutation_data["mutated_code"]
    )
    _write_file(target_file, modified_content)


def _execute_simulation(run_sim_path, sim_command):
    cmd = f"cd {run_sim_path} && {sim_command}"
    subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True)


def _collect_simulation_results(
    run_sim_path, results_dir, output_file, sim_result_path, log_glob
):
    output_path = os.path.join(run_sim_path, output_file)
    if os.path.exists(output_path):
        subprocess.run(
            f"cp {output_path} {results_dir}/", shell=True, executable="/bin/bash"
        )

    log_files_path = os.path.join(sim_result_path, log_glob)
    subprocess.run(
        f"cp {log_files_path} {results_dir}/ 2>/dev/null || true",
        shell=True,
        executable="/bin/bash",
    )


def _clean_simulation_artifacts(
    run_sim_path, output_file, sim_result_path, clean_commands
):
    # Remove output file.
    output_path = os.path.join(run_sim_path, output_file)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Run each clean command.
    for cmd in clean_commands:
        subprocess.run(
            f"cd {sim_result_path} && {cmd}",
            shell=True,
            executable="/bin/bash",
            capture_output=True,
        )


def get_relative_path(path, design_root_name):
    if design_root_name in path:
        parts = path.split(design_root_name)
        if len(parts) > 1 and parts[1]:
            return parts[1][1:] if parts[1].startswith("/") else parts[1]
    return ""


def run_simulation(design_copy_path, mutation, config):
    design_copy_path = os.path.abspath(design_copy_path)
    file_path, mutation_data = mutation

    # Update paths to be relative to design copy.
    design_root_name = os.path.basename(config["design_root_path"])

    # Update paths to be relative to design copy.
    relative_file_path = get_relative_path(file_path, design_root_name)
    target_file = os.path.join(design_copy_path, relative_file_path)

    run_sim_relative_path = get_relative_path(config["run_sim_path"], design_root_name)
    run_sim_path = os.path.join(design_copy_path, run_sim_relative_path)

    sim_result_relative_path = get_relative_path(config["sim_result_path"], design_root_name)
    sim_result_path = os.path.join(design_copy_path, sim_result_relative_path)

    # Create unique ID for this mutation.
    unique_id = f"{os.path.basename(file_path)}_{mutation_data['mutation_type']}_{hash(mutation_data['original_code'])}"
    results_dir = os.path.join("results", unique_id)
    results_dir = os.path.abspath(results_dir)
    os.makedirs(results_dir, exist_ok=True)

    # Backup original content, apply mutation.
    original_content = read_file(target_file)
    _apply_mutation(target_file, mutation_data)

    print(f"-- Running simulation in {design_copy_path} with mutation in {target_file}")
    _execute_simulation(run_sim_path, config["sim_command"])

    _collect_simulation_results(
        run_sim_path,
        results_dir,
        config["output_file"],
        sim_result_path,
        config["log_glob"],
    )
    _clean_simulation_artifacts(
        run_sim_path,
        config["output_file"],
        sim_result_path,
        config["clean_commands"],
    )

    # Restore original content.
    _write_file(target_file, original_content)

    return {unique_id: {"target_file": os.path.basename(file_path)} | mutation_data}


def run_simulations():
    create_results_directory()

    # Load configuration and mutations.
    config = read_json("config.json")
    mutations = read_json("mutations.json")

    design_root_path = config["design_root_path"]
    # num_jobs = int(config.get("num_jobs", 1)) # TODO: Implement multi-job support

    # Prepare mutation tuples.
    mutation_tuples = []
    for target_file, target_mutations in mutations.items():
        for target_mutation in target_mutations:
            mutation_tuples.append((target_file, target_mutation))

    total_mutations = len(mutation_tuples)

    # Create design copy.
    design_copy_path = spawn_design_copy(design_root_path)

    print(f"-- Starting simulations for {total_mutations} mutations sequentially...")

    # Execute simulations iteratively.
    results = {}
    completed_count = 0
    failed_count = 0

    for mutation in mutation_tuples:
        try:
            result = run_simulation(design_copy_path, mutation, config)
            results.update(result)
            completed_count += 1
            print(
                f"-- Progress: {completed_count}/{total_mutations} simulations completed."
            )

            # Dump intermediate results every 5 mutations.
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
