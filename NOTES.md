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
- [ ] Get details about Certitude bug types. Dive deep into the tool itself.
- [x] Do code interpreter & file search improve output?
    File search is useless in our case. On top of that, it cannot access .sv files.
    Code interpreter may be beneficial even if it does not run Verilog natively.
- [ ] Try changing the configuration of the assistant: a) using code interpreter and b) removing the explanation field.
- [ ] Sliding window with stuck-at-0 to measure the success rate:
        Compare small vs large files
        Window size -> n number of lines
        Success -> # of successful replacements & runs on the hello world test -> #successful_runs / #total_runs
        Preprocessing: remove all comments & whitespaces
- [ ] Run UVM Tests following Mike's instructions
- [ ] Integrate Dromajo into the CV32E40P environment
- [ ] Determine binary files used for verification
- [ ] Find how to get coverage information from Questa

<!-- Imperas... ???? -->
vendor_lib/imperas/imperas_DV_COREV/sv/imperas_CV32.sv
vendor_lib/imperas/imperas_DV_COREV/README.md:
vendor_lib/imperas/imperas_DV_COREV/ChangeLog.md
vendor_lib/imperas/design/typedefs.sv
vendor_lib/imperas/design/monitor.sv
vendor_lib/imperas/design/ram.sv

<!-- SystemVerilog Testbench configs -->
vendor_lib/verissimo/waivers.xml

<!-- ??? -->
.metrics.json

<!-- DOCS -->
docs/VerifStrat/source/cv32_env.rst
docs/VerifStrat/source/quick_start.rst
docs/VerifStrat/source/pulp_verif.rst

<!-- Reusable verification components: UVM Agents: ??? -->
lib/uvm_agents/uvma_core_cntrl/uvma_core_cntrl_cfg.sv
lib/uvm_agents/uvma_rvvi_ovpsim/uvma_rvvi_ovpsim_agent.sv

<!-- Common makefiles -->
mk/README.md
[!!!] mk/Common.mk
mk/uvmt/vcs.mk
mk/uvmt/riviera.mk
[!!!] mk/uvmt/uvmt.mk
mk/uvmt/dsim.mk
mk/uvmt/xrun.mk
[!!!] mk/uvmt/vsim.mk
mk/uvmt/dvt.mk
[!!!] mk/core/core.mk


<!-- Source files used to support the Imperas ISS -->
cv32e40p/vendor_lib/imperas/riscv_CV32E40P_OVPsim/sv/riscv_CV32E40P.h
cv32e40p/vendor_lib/imperas/riscv_CV32E40P_OVPsim/sv/riscv_datatype.h
cv32e40p/vendor_lib/README.md

<!-- Imperas ISS options -->
cv32e40p/tests/cfg/pulp.yaml

<!-- Tests: ??? -->
cv32e40p/tests/programs/custom/all_csr_por/all_csr_por.c
cv32e40p/tests/programs/custom/modeled_csr_por/modeled_csr_por.c
cv32e40p/tests/programs/custom/requested_csr_por/requested_csr_por.c
cv32e40p/tests/programs/custom/fibonacci/fibonacci.c

<!-- Tool specific sub-dirs for some of the tools used in the CV32E40P -->
cv32e40p/sim/tools/imperas/README.md
cv32e40p/sim/tools/README.md
cv32e40p/sim/tools/xrun/restore.tcl
cv32e40p/sim/tools/xrun/restore.tcl.svcf

<!-- Testbench: Testbench for CV32E40P:  -->
<!-- Module wrapper for Imperas OVP -->
cv32e40p/tb/uvmt/uvmt_cv32e40p_iss_wrap.sv
<!-- Step and Compare between the CV32E40P and Imperas OVPsim -->
cv32e40p/tb/uvmt/uvmt_cv32e40p_step_compare.sv

cv32e40p/tb/uvmt/imperas_iss.flist
<!-- Coverage model ??? -->
cv32e40p/env/uvme/cov/uvme_rv32isa_covg.sv


binary
compatibility
no imperas yes dromajo - what files should we change