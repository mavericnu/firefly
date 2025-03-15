# Copyright (c) 2024 Maveric @ NU and Texer.ai. All rights reserved.
import os
import yaml
from pathlib import Path


def generate_config_file(ma_path, rtl_path, target_files):
    config = {
        "ma_path": str(ma_path),
        "rtl_path": str(rtl_path),
        "target_files": target_files,
        "cmd": "",
        "sim_path": "",
        "num_jobs": "",
    }

    config_path = Path("firefly.yml")
    with open(config_path, "w") as f:
        yaml.safe_dump(
            {
                "ma_path": config["ma_path"],
                "rtl_path": config["rtl_path"],
                "target_files": config["target_files"],
            },
            f,
            default_flow_style=False,
            sort_keys=False,
        )
        f.write("\n")
        yaml.safe_dump(
            {"cmd": config["cmd"], "sim_path": config["sim_path"]},
            f,
            default_flow_style=False,
            sort_keys=False,
        )
        f.write("\n")
        yaml.safe_dump(
            {"num_jobs": config["num_jobs"]},
            f,
            default_flow_style=False,
            sort_keys=False,
        )

    print(f"\nConfiguration file generated: {config_path.absolute()}")


def scan_rtl_directory(path):
    sv_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".sv") or file.endswith(".v"):
                sv_files.append(str(Path(root) / file))

    if sv_files:
        print(f"\nFound {len(sv_files)} Verilog/SystemVerilog file(s).")
    else:
        print("\nNo SystemVerilog (.sv) files found in the specified directory.")

    return sv_files


def get_valid_directory_path(prompt):
    while True:
        path = input(prompt).strip()
        path = Path(path).resolve()

        if not path.exists():
            print(f"Error: Directory '{path}' does not exist. Please try again.")
            continue

        if not path.is_dir():
            print(f"Error: '{path}' is not a directory. Please try again.")
            continue

        return path


def get_paths():
    ma_path = get_valid_directory_path(
        "Please enter the absolute path to the microarchitecture root: "
    )
    rtl_path = get_valid_directory_path(
        "Please enter the absolute path to the RTL directory: "
    )
    return ma_path, rtl_path


def main():
    ma_path, rtl_path = get_paths()
    sv_files = scan_rtl_directory(rtl_path)
    if not sv_files:
        print("\nExiting: No Verilog/SystemVerilog files found.")
        return 1

    generate_config_file(ma_path, rtl_path, sv_files)
    return 0


if __name__ == "__main__":
    exit(main())
