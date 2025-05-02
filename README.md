# Firefly: AI-Assisted Verilog Mutation Testing

## Overview

Firefly is an AI-assisted mutation testing framework designed to enhance the robustness of hardware verification environments for designs written in Verilog or SystemVerilog. By leveraging an LLM (Google Gemini) to create semantically relevant code mutations, Firefly helps uncover subtle bugs and weaknesses in testbenches and verification strategies.

It automates the process of configuring tests, generating diverse mutations, running simulations for each mutant, and collecting the results.

### Why use Firefly?

*   **Enhance Verification:** Go beyond standard testbenches by injecting complex, AI-generated faults into your design.
*   **Identify Weaknesses:** Discover gaps in your test suite where specific design bugs might go undetected.
*   **Automate Mutation Testing:** Streamline the traditionally manual and time-consuming process of mutation testing for hardware.
*   **Improve Design Robustness:** Systematically test how your design and verification environment handle various fault types.

### Key Features

1.  **AI-Powered Mutation:** Utilizes Google's Gemini model to generate high-impact, semantically aware Verilog/SystemVerilog mutations (e.g., FSM corruption, pipeline hazards, timing issues).
2.  **Automated Workflow:** Provides commands (`prep`, `mutate`, `run`) to manage the end-to-end mutation testing process.
3.  **Configurable:** Uses JSON files (`config.json`, `mutations.json`) for easy setup and management of simulation parameters, target files, and generated mutations.
4.  **Simulation Integration:** Works with user-specified Verilog simulators and simulation commands.
5.  **Results Management:** Creates dedicated directories for simulation results of each mutation and compiles a summary (`results/ids.json`).
6.  **Targeted Fault Types:** Focuses on realistic hardware bug categories like FSM state transition errors, pipeline control logic issues, timing violations, and fault injections.
7.  **API Rate Limiting & Retries:** Includes built-in handling for generative AI API usage limits.

## Installation and Usage

### Prerequisites

*   Python 3.x
*   Access to a Verilog/SystemVerilog simulator
*   Google Generative AI API access (and corresponding key configured)
*   Standard Unix command-line tools (`cp`, `bash`)

### Installation

1.  Clone the repository:
    ```bash
    git clone <your-repository-url> # Replace with actual URL
    cd firefly
    ```

2.  Install Python dependencies:
    ```bash
    pip install google-generativeai
    ```

3.  Configure Google Generative AI: Ensure your API key is set up correctly for the `google-generativeai` library (e.g., via environment variables). Refer to the [Google AI documentation](https://ai.google.dev/docs).

### Usage

Firefly operates through three main commands:

1.  **Prepare (`prep`):**
    *   Scans for Verilog/SystemVerilog files.
    *   Prompts the user for configuration details (design paths, simulation command, number of mutations, output paths, clean commands, etc.).
    *   Creates `config.json` with the settings.
    *   Creates the `sim/` directory.
    ```bash
    python firefly.py prep
    ```
    Follow the interactive prompts to configure your simulation environment.

2.  **Mutate (`mutate`):**
    *   Reads `config.json`.
    *   Uses the configured AI model to generate Verilog mutations for the target files.
    *   Handles API rate limits and retries for generation.
    *   Saves the generated mutations to `mutations.json`.
    ```bash
    python firefly.py mutate
    ```

3.  **Run (`run`):**
    *   Reads `config.json` and `mutations.json`.
    *   Creates a copy of the design in `sim/`.
    *   Iterates through each mutation:
        *   Applies the mutation to the design copy.
        *   Executes the user-defined simulation command.
        *   Collects simulation outputs (logs, result files) into `results/<mutation_id>/`.
        *   Cleans simulation artifacts.
        *   Restores the original code in the design copy.
    *   Saves a summary of executed mutations to `results/ids.json`.
    ```bash
    python firefly.py run
    ```

Check the `results/` directory for the outcome of each mutation simulation. The `ids.json` file provides a map between the unique mutation ID (used for the directory name) and the details of the applied mutation. 