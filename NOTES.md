FOR THE APPROACH WITH UNIQUE IDENTIFIERS, 2 ASSISTANTS ARE REQUIRED:
    for parsing/analyzing module + identifying code snippets prone to bugs
    for introducing a bug to the previously identified place


POTENTIAL PIPELINE:
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


BUG TYPES:
    stuck-at zero
    2-cycle delay
    classical human engineering error
    connectivity fault


ISSUE RELATED TO APPROACH #2:
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


MAKE SURE TO INCLUDE:
    specific bug types
    prioritize Verilog syntax
    emphasize synthesizability
    code context
    example JSON response


[] how does code interpreter work?
[] do code interpreter & file search improve output?
    * file search cannot access .sv files



You are a part of a mutation testing system for hardware designs written in Verilog. Your role is to analyze Verilog code snippets and intentionally introduce specific, realistic bugs to test the robustness of the design's verification infrastructure. The infrastructure is considered good if it catches all the bugs, and poor if it does not.

Your task is to introduce ONE bug from the following list to the provided Verilog code:
- **  **
- **  **
- **  **

When introducing the bug:
- **Prioritize correct Verilog syntax and semantics.** The bug should be subtle and realistic.
- **Consider the context of the provided code snippet.** A bug must be relevant within the larger module.

