# Copyright (c) 2025 Maveric @ NU and Texer.ai. All rights reserved.
import argparse
from src.prep import prep_simulation
from src.mutate import spawn_mutations
from src.run import run_simulations


def parse_args():
    parser = argparse.ArgumentParser(
        description="Firefly is an AI-assisted mutation testing system for hardware designs written in Verilog.",
    )

    parser.add_argument(
        "command",
        choices=["prep", "mutate", "run"],
        help="The command to execute.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    if args.command == "prep":
        success = prep_simulation()
        if not success:
            print("Failed to prepare simulation.")
            return 1
    elif args.command == "mutate":
        success = spawn_mutations()
        if not success:
            print("Failed to generate mutations.")
            return 1
    elif args.command == "run":
        success = run_simulations()
        if not success:
            print("Failed to run simulations.")
            return 1
    else:
        print("Invalid command.")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
