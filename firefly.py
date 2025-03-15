# Copyright (c) 2024 Maveric @ NU and Texer.ai. All rights reserved.
from src.prep import prep_simulation


def main():
    success = prep_simulation()
    if not success:
        print("Failed to prepare simulation.")
        return 1

    # TODO: Mutate
    # TODO: Run simulation

    return 0


if __name__ == "__main__":
    exit(main())
