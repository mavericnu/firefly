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

# Questionably better workflow:
... -> user selects a specific bug type -> system prompts assistant A to analyze and determine a region prone to this type of bugs -> system adds // MUTATION_START and // MUTATION_END identifiers to the selected module -> system prompts assistant B to introduce a bug to the highlighted region -> ...
* system can save information about the region to avoid try duplication


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


# Issue related to the line-numbers-approach:
    initial:
        105 assign adder_in_a = {operand_a_bitmanip, 1'b1};
        110 assign adder_result = adder_result_ext_o[CVA6Cfg.XLEN:1];
    modified:
        105 logic [CVA6Cfg.XLEN:0] adder_in_a_d1, adder_in_a_d2;
        106 always_ff @(posedge clk_i) begin
        107 if (!rst_ni) begin
        108 adder_in_a_d1 <= {CVA6Cfg.XLEN{1'b0}};
        109 adder_in_a_d2 <= {CVA6Cfg.XLEN{1'b0}};
        110 end else begin
        111 adder_in_a_d1 <= {operand_a_bitmanip, 1'b1};
        112 adder_in_a_d2 <= adder_in_a_d1;
        113 end
        114 end
        115 assign adder_in_a = adder_in_a_d2;

        110 logic [CVA6Cfg.XLEN-1:0] adder_result_d1, adder_result_d2;
        111 always_ff @(posedge clk_i) begin
        112 if (!rst_ni) begin
        113 adder_result_d1 <= {CVA6Cfg.XLEN{1'b0}};
        114 adder_result_d2 <= {CVA6Cfg.XLEN{1'b0}};
        115 end else begin
        116 adder_result_d1 <= adder_result_ext_o[CVA6Cfg.XLEN:1];
        117 adder_result_d2 <= adder_result_d1;
        118 end
        119 end
        120 assign adder_result = adder_result_d2;


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

# Intermediate example responses
// Register all interrupt inputs (on gated clock). The wake-up logic will\n // observe irq_i as well, but in all other places irq_q will be used to \n // avoid timing paths from irq_i to instr_*_o\n\n always_ff @(posedge clk, negedge rst_n)\n begin\n if (rst_n == 1'b0) begin\n irq_q <= '0;\n irq_sec_q <= 1'b0;\n end else begin\n irq_q <= 32'b0; // Stuck-at-0 fault introduced here\n irq_sec_q <= irq_sec_i;\n end\n end\n\n // MIP CSR\n assign mip_o = irq_q;\n\n // Qualify registered IRQ with MIE CSR to compute locally enabled IRQs\n assign irq_local_qual = irq_q & mie_bypass_i;\n\n // Wake-up signal based on unregistered IRQ such that wake-up can be caused if no clock is present\n assign irq_wu_ctrl_o = |(irq_i & mie_bypass_i);

// Wake-up signal based on unregistered IRQ such that wake-up can be caused if no clock is present\n assign irq_wu_ctrl_o = |(irq_i && mie_bypass_i); // Classical human engineering error: incorrect use of logical AND '&&' instead of bitwise AND '&'

"description": "To introduce a 2-cycle delay in the interrupt ID assignment logic, I will modify the code such that the assignment to irq_id_ctrl_o is delayed by two clock cycles. This can be done by adding two registers to hold the intermediate values for two cycles before the final value is assigned to irq_id_ctrl_o. This will delay IRQ response, introducing subtle timing issues.", "code": " logic [4:0] irq_id_ctrl_intermediate1;\n logic [4:0] irq_id_ctrl_intermediate2;\n\n always_ff @(posedge clk, negedge rst_n)\n begin\n if (rst_n == 1'b0) begin\n irq_id_ctrl_intermediate1 <= 5'd0;\n irq_id_ctrl_intermediate2 <= 5'd0;\n irq_id_ctrl_o <= 5'd0;\n end else begin\n irq_id_ctrl_intermediate1 <= irq_id_ctrl_intermediate2;\n irq_id_ctrl_intermediate2 <= irq_local_qual[31] ? 5'd31 :\n irq_local_qual[30] ? 5'd30 :\n irq_local_qual[29] ? 5'd29 :\n irq_local_qual[28] ? 5'd28 :\n irq_local_qual[27] ? 5'd27 :\n irq_local_qual[26] ? 5'd26 :\n irq_local_qual[25] ? 5'd25 :\n irq_local_qual[24] ? 5'd24 :\n irq_local_qual[23] ? 5'd23 :\n irq_local_qual[22] ? 5'd22 :\n irq_local_qual[21] ? 5'd21 :\n irq_local_qual[20] ? 5'd20 :\n irq_local_qual[19] ? 5'd19 :\n irq_local_qual[18] ? 5'd18 :\n irq_local_qual[17] ? 5'd17 :\n irq_local_qual[16] ? 5'd16 :\n irq_local_qual[15] ? 5'd15 :\n irq_local_qual[14] ? 5'd14 :\n irq_local_qual[13] ? 5'd13 :\n irq_local_qual[12] ? 5'd12 :\n irq_local_qual[CSR_MEIX_BIT] ? CSR_MEIX_BIT :\n irq_local_qual[CSR_MSIX_BIT] ? CSR_MSIX_BIT :\n irq_local_qual[CSR_MTIX_BIT] ? CSR_MTIX_BIT :\n irq_local_qual[10] ? 5'd10 :\n irq_local_qual[ 2] ? 5'd2 :\n irq_local_qual[ 6] ? 5'd6 :\n irq_local_qual[ 9] ? 5'd9 :\n irq_local_qual[ 1] ? 5'd1 :\n irq_local_qual[ 5] ? 5'd5 :\n irq_local_qual[ 8] ? 5'd8 :\n irq_local_qual[ 0] ? 5'd0 :\n irq_local_qual[ 4] ? 5'd4 :\n CSR_MTIX_BIT;\n irq_id_ctrl_o <= irq_id_ctrl_intermediate1;\n end\n end"

# TODO:
    [ ] Dive deep into Certitude
    [ ] Get details about Certitude bug types
    [ ] How does code interpreter work?
    [ ] Do code interpreter & file search improve output? --> *file search cannot access .sv files
    [ ] Sliding window with stuck-at-0 to measure the success rate:
        Compare small vs large files
        Window size -> n number of lines
        Success -> # of successful replacements & runs on the hello world test -> #successful_runs / #total_runs