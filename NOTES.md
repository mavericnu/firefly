2 APPROACHES:
    1. using unique markers
        ```
        // BEGIN_MUTATION_BLOCK
        ...
        // END_MUTATION_BLOCK
        ```
    2. line numbers
        ```
        5 EQ:       alu_branch_res_o = adder_z_flag;
        ```


FOR APPROACH 1, 2 ASSISTANTS ARE REQUIRED:
    for parsing/analyzing module + identifying code snippets prone to bugs
    for introducing a bug to the previously identified place


POTENTIAL PIPELINE:
    1. system outputs a list of modules
    2. user selects a module to modify
    3. system starts an assistant session for this single module
    4. user selects the type and/or the number of bugs
    5. user selects the number of parallel workers
    6. user starts the verification
        1. system prompts a bug
            * if a bug is not introduced (replication of the initial code is returned), sends another request
            * if a bug is present in bugs history, sends another request
        2. system introduces a bug
        3. system runs a test suite 


BUG TYPES:
    stuck-at zero
    2-cycle delay
    classical human engineering error
    connectivity fault