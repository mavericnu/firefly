# Copyright (c) 2025 Maveric @ NU and Texer.ai. All rights reserved.
import json
import os

from pathlib import Path


# Define all functions.
def generate_json_config(config):
    json_path = Path("config.json")
    with open(json_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"-- JSON config file generated at '{json_path.absolute()}'.")


def scan_rtl_directory(path):
    sv_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".sv") or file.endswith(".v"):
                sv_files.append(str(Path(root) / file))

    if sv_files:
        print(f"-- Found {len(sv_files)} Verilog/SystemVerilog file(s).")
    else:
        print("-- No Verilog/SystemVerilog files found in the specified directory.")

    return sv_files


def get_valid_directory_path(prompt):
    while True:
        path = input(prompt).strip()
        path = Path(path).resolve()

        if not path.exists():
            print(f"-- Directory '{path}' does not exist. Please try again.")
            continue

        if not path.is_dir():
            print(f"-- Path '{path}' is not a directory. Please try again.")
            continue

        return path


def get_paths():
    design_root_path = get_valid_directory_path(
        "Enter the absolute path to the design root directory: "
    )
    rtl_path = get_valid_directory_path(
        "Enter the absolute path to the RTL directory: "
    )
    return design_root_path, rtl_path


def get_simulation_parameters():
    num_mutations = input("How many mutations to apply to the design?: ")
    sim_command = input("How to run the simulation?: ")
    run_sim_path = get_valid_directory_path(
        "Enter the absolute path to the directory from which to run the simulation: "
    )
    sim_result_path = get_valid_directory_path(
        "Enter the absolute path to the directory where simulation results are stored: "
    )
    output_file = input(
        "Enter the name of the output file. It is expected to be in the directory from which the simulation is run: "
    )
    log_glob = input("Enter the glob pattern for log files: ")
    clean_commands = input(
        "Enter the commands separated by semicolons to clean simulation artifacts: "
    ).split(";")
    num_jobs = input("How many simulations to run in parallel?: ")
    return (
        num_mutations,
        sim_command,
        run_sim_path,
        sim_result_path,
        output_file,
        log_glob,
        clean_commands,
        num_jobs,
    )


def create_simulation_directory():
    sim_path = Path("sim")
    if sim_path.exists():
        print(f"-- Simulation directory already exists at '{sim_path.absolute()}'.")
        return

    sim_path.mkdir(parents=True, exist_ok=True)
    print(f"-- Simulation directory created at '{sim_path.absolute()}'.")


def prep_simulation():
    design_root_path, rtl_path = get_paths()
    sv_files = scan_rtl_directory(rtl_path)
    if not sv_files:
        return False
    (
        num_mutations,
        sim_command,
        run_sim_path,
        sim_result_path,
        output_file,
        log_glob,
        clean_commands,
        num_jobs,
    ) = get_simulation_parameters()

    config = {
        "design_root_path": str(design_root_path),
        "num_mutations": num_mutations,
        "sim_command": sim_command,
        "run_sim_path": str(run_sim_path),
        "sim_result_path": str(sim_result_path),
        "output_file": output_file,
        "log_glob": log_glob,
        "clean_commands": clean_commands,
        "num_jobs": num_jobs,
        "target_files": sv_files,
    }
    generate_json_config(config)
    create_simulation_directory()
    return True
