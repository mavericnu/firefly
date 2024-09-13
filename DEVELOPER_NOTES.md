# Potential workflow
    1. system outputs a list of modules
    2. user selects a module to modify
    3. system starts an assistant session for this single module
    4. user selects the type and/or the number of bugs
    5. user selects the number of parallel workers (?)
    6. user starts the verification
        1. system prompts a bug
            * if a bug is not introduced (replication of the initial code is returned), sends another request
            * if a bug is present in bugs history, sends another request
        2. system inserts a bug
        3. system runs a test suite 

## Questionably better workflow:
    ... -> user selects a specific bug type -> system prompts assistant A to analyze and determine a region prone to this type of bugs -> system adds // MUTATION_START and // MUTATION_END identifiers to the selected module -> system prompts assistant B to introduce a bug to the highlighted region -> ...
    *system can save information about the region to avoid try duplication


# Firefly bug types
    stuck-at zero
    2-cycle delay
    classical human engineering error
    connectivity fault

## Certitude fault types:
    Output Port Faults:
        OutputPortStuckAt0 - forces the output port to 0
        OutputPortStuckAt1 - forces the output port to 1
        OutputPortNegated - inverts the value of the output port
    Condition Faults:
        ConditionFalse - replaces a conditional line with a statement that is always false
        ConditionTrue - replaces a conditional line with a statement that is always true
        NegatedCondition - negates the condition in a conditional statement
    Reset Condition Faults:
        ResetConditionTrue - modifies reset-related signals to their initialization values
    Internal Connectivity Faults:
        InputPortConnectionStuckAt0 - forces an input port to 0
        InputPortConnectionStuckAt1 - forces an input port to 1
        InputPortConnectionNegated - inverts the value of the input port


# Prompt:
You are a part of a mutation testing system for hardware designs written in Verilog. Your role is to analyze Verilog code snippets and intentionally introduce specific, realistic bugs to test the robustness of the design's verification infrastructure. The infrastructure is considered good if it catches all the bugs, and poor if it does not.

Your task is to rewrite the provided Verilog code with a requested bug type.

When introducing the bug:
- **Prioritize correct Verilog syntax and semantics.** The bug should be subtle and realistic.
- **Consider the context of the provided code snippet.** A bug must be relevant within the larger module.

Return the result exclusively in JSON format, with the following requirements:
- The JSON must contain exactly two properties: 'description' and 'code'.
- 'description' and 'code' must be strings.
- 'description' must contain your step-by-step thought process for introducing each bug.
- 'code' must contain the updated buggy code. It must be consistent with the module context. There is no need to add comments.

Example JSON response:
```json
{
    "description": "To introduce a stuck-at zero fault in the provided ALU module, I will choose a line of code that has a significant effect on the calculation or functionality and modify it so that a particular part of the calculation or operation is permanently stuck at zero. Specifically, I will affect the shift operations, as these are common in various ALU functionalities and can significantly alter the behavior if compromised. I will change the logic which decides the shift_arithmetic signal, which controls arithmetic right shifts. Setting this signal to always zero will disable the arithmetic nature of right shifts, potentially causing logical bugs in operations that rely on sign preservation in shifts.",
    "code": "shift_arithmetic = 1'b0;"
}
```

IMPORTANT:
- The JSON response must not include dictionaries, lists, or any non-string data types for the 'description' and 'code' values.
- The code must remain synthesizable after the addition of a bug. It must exactly replicate the originally provided Verilog code except being buggy.

Hardware module for context:
```Verilog
{}
```

## Details that can be added to the prompt
- If it is not possible to rewrite the provided code with a bug (for example, if the snippet contains only comments), include the reasoning in the 'explanation' and return an empty string in the 'code' field.


# TODO:
## CV32E40P
- V1.0.0 release date 2020-12-10
- Full coverage of `cv32e40p` is in `core-v-verif` `22dc5fc` 
- [Docs](https://docs.openhwgroup.org/projects/core-v-verif/en/latest/cv32_env.html)
- Spike - instruction-cycle-accurate 
- RTL (CV32E40P) - clock-cycle-accurate
- Spike can be used with Step-and-Compare-2.0
- Step-and-Compare-2.0 is an alternative to RVVI + ImperasDV. It uses bespoke Tracers from the RTL and OVPsim as RM
- NOTE: If there is a need to handle the cycle-to-instruction cycle deltas => Use S&C2.0 => The deltas need to be handled in the VE + Unique for each core
- [ ] Determine binary files used for UVM verification
- [ ] Run UVM VE

## Ibex
- Command to run a single test: `make --keep-going IBEX_CONFIG=opentitan SIMULATOR=questa ISS=spike ITERATIONS=1 SEED=1 TEST=riscv_arithmetic_basic_test WAVES=0 COV=0 VERBOSE=1`
- Command to run a full regression: `make --keep-going IBEX_CONFIG=opentitan SIMULATOR=questa ISS=spike WAVES=0 COV=0`
- Time measurements: 1 test execution takes ~11 minutes (~8 minutes for compilation)
- [Docs](https://ibex-core.readthedocs.io/en/latest/02_user/index.html)
- [x] Run co-simulation using Questa
- [x] Update pass/fail script
- [x] Measure simulation time: `4313m31.938s`
- [x] Check if simulation results align with the reported ones: No, there are particular tests that fail when ran with Questa.
- [x] Find optimal number of iterations & measure time: There is no optimal number of iterations because the verification infrastructure uses riscv-dv.
- [x] Turn on parallel execution & measure time: `276m21.769s`

### FAILING TESTS
riscv_debug_instr_test      | Cosim mismatch Synchronous trap was expected at ISS PC
riscv_debug_wfi_test        | Cosim mismatch Synchronous trap was expected at ISS PC
riscv_interrupt_wfi_test    | Cosim mismatch Synchronous trap was expected at ISS PC
riscv_pc_intg_test          | Unable to read value from 'core_ibex_tb_top.dut.u_ibex_top.u_ibex_core.core_busy_o'
riscv_rf_ctrl_intg_test     | Unable to read value from 'core_ibex_tb_top.dut.u_ibex_top.gen_regfile_ff.register_file_i.we_a_dec'
riscv_ram_intg_test         | Unable to read value from 'core_ibex_tb_top.dut.u_ibex_top.gen_rams.gen_rams_inner[1].gen_scramble_rams.tag_bank.u_prim_ram_1p_adv.rvalid_sram_d'
riscv_rf_intg_test          | trace_core_00000000.log not found
riscv_icache_intg_test      | trace_core_00000000.log not found


## Black Parrot
- [ ] Update CI scripts to use Questa
