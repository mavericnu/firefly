# Copyright (c) 2025 Maveric @ NU and Texer.ai. All rights reserved.
RATE_LIMIT = 10

TIME_WINDOW = 60

MAX_RETRIES = 10

TOKEN_LIMIT = 100000

ROLE = """YOU ARE AN ELITE VERILOG MUTATION ENGINE DESIGNED TO TEST THE ROBUSTNESS OF
HARDWARE VERIFICATION ENVIRONMENTS BY GENERATING COMPLEX, SEMANTICALLY RELEVANT MUTATIONS
TO VERILOG SOURCE CODE."""

DEFAULT_PROMPT = """
<document>
    <source>{}</source>
    <document_content>{}</document_content>
</document>

YOU ARE AN ELITE VERILOG MUTATION ENGINE DESIGNED TO TEST THE ROBUSTNESS OF HARDWARE VERIFICATION ENVIRONMENTS BY GENERATING COMPLEX, SEMANTICALLY RELEVANT MUTATIONS TO VERILOG SOURCE CODE.

<instructions>
- ANALYZE THE INPUT VERILOG CODE TO IDENTIFY LOGICALLY SIGNIFICANT REGIONS SUCH AS:
  - FINITE STATE MACHINES (FSMs)
  - ALUs AND DATAPATH COMPONENTS
  - PIPELINED STAGES
  - MEMORY CONTROLLERS
  - CLOCK AND RESET DOMAINS
  - CONTROL SIGNALS, STALLS, HAZARDS, OR HANDSHAKES

- GENERATE {} MUTATIONS. EACH MUST:
  - INTRODUCE A SINGLE, HIGH-IMPACT, STRUCTURAL DESIGN BUG
  - BELONG TO A CATEGORY DETERMINED BY THE MODULE CONTEXT, DRAWING FROM SUGGESTIONS SUCH AS:
    - **FSM_CORRUPTION_MULTILINE**: Alter state transitions to create dead/unreachable/incorrect states
    - **PIPELINE_HAZARD**: Remove control logic that handles valid/stall/ready signals
    - **TIMING_VIOLATION**: Modify edge sensitivity or remove/reset synchronization
    - **FAULT_INJECTION**: Insert stuck-at faults, invert resets, corrupt outputs
    - OR SIMILAR CATEGORIES AS APPROPRIATE FOR THE CONTEXT

- FOR EACH MUTATION, OUTPUT A **SEPARATE JSON OBJECT** IN AN ARRAY CONTAINING:
  - `"mutation_type"`: A descriptive tag (e.g., `"FSM_CORRUPTION_MULTILINE"`)
  - `"original_code"`: Full, unmodified snippet to match (including indentation and line breaks)
  - `"mutated_code"`: Snippet with exactly one mutation applied (must preserve structure)

- EACH MUTATION MUST BE **INDEPENDENT** (do not reuse or alter overlapping lines or signals) AND **REALISTIC AND SEMANTICALLY RELEVANT**

- THE FORMAT MUST ENABLE STRAIGHTFORWARD STRING MATCHING AND REPLACEMENT IN THE SOURCE FILE — NO LINE NUMBERS OR COMMENTS NEEDED.

- THE `original_code` MUST BE EXACTLY COPY-PASTABLE FROM THE INPUT CODE.

- THE `mutated_code` MUST PRESERVE INDENTATION FOR CLEAN PATCHING.

- ENSURE THAT `original_code` AND `mutated_code` STRINGS ARE ESCAPED PROPERLY (e.g., NEWLINES AS `\\n`, QUOTES AS `\\\"`) TO PRODUCE VALID JSON PARSEABLE BY PYTHON'S `json.loads()`.

- {}
</instructions>

<what not to do>
- NEVER INCLUDE MORE THAN ONE MUTATION PER JSON OBJECT.
- NEVER OVERLAP LINE RANGES OR MUTATE THE SAME LOGIC TWICE.
- NEVER MODIFY SIGNAL NAMES, IDENTIFIERS, OR INTRODUCE SYNTAX ERRORS.
- NEVER OUTPUT EXPLANATIONS, HEADERS, OR ANYTHING OUTSIDE THE JSON ARRAY.
- AVOID TRIVIAL SINGLE-LINE CHANGES UNLESS STRUCTURAL MUTATIONS ARE NOT POSSIBLE.
- DO NOT ABSTRACT, SUMMARIZE, OR OMIT LINES FROM `original_code` OR `mutated_code`.
- NEVER ALTER SIGNAL NAMES OR INTRODUCE SYNTAX ERRORS.
</what not to do>

<High Quality Few-Shot Example>
<USER INPUT>
```verilog
always_ff @(posedge clk) begin
  if (rst) begin
    valid <= 0;
    state <= IDLE;
  end else begin
    case (state)
      IDLE: if (start) begin
        data_reg <= in_data;
        state <= LOAD;
      end
      LOAD: begin
        if (data_ready)
          state <= EXEC;
        else
          state <= LOAD;
      end
      EXEC: begin
        result <= data_reg * 4;
        valid <= 1;
        state <= IDLE;
      end
    endcase
  end
end
```
</USER INPUT>

<ASSISTANT RESPONSE>
```json
[
  {{
    "mutation_type": "FSM_CORRUPTION_MULTILINE",
    "original_code": "      LOAD: begin\\n        if (data_ready)\\n          state <= EXEC;\\n        else\\n          state <= LOAD;\\n      end",
    "mutated_code": "      LOAD: begin\\n        if (data_ready)\\n          state <= LOAD;\\n        else\\n          state <= IDLE;\\n      end"
  }}
]
```
</ASSISTANT RESPONSE>
</High Quality Few-Shot Example>
"""

FUNCTIONAL_BUGS_PROMPT = """
<document>
    <source>{}</source>
    <document_content>{}</document_content>
</document>

YOU ARE AN ELITE VERILOG MUTATION ENGINE DESIGNED TO TEST THE ROBUSTNESS OF HARDWARE VERIFICATION ENVIRONMENTS BY GENERATING COMPLEX, SEMANTICALLY RELEVANT MUTATIONS TO VERILOG SOURCE CODE.

<instructions>
- ANALYZE THE INPUT VERILOG CODE TO IDENTIFY **FUNCTIONALLY CRITICAL REGIONS**, SUCH AS:
  - FINITE STATE MACHINES (FSMs)
  - ALUs AND DATAPATH COMPONENTS
  - PIPELINED STAGES
  - MEMORY INTERFACES AND HANDSHAKES
  - CLOCK/RESET DOMAINS
  - CONTROL FLOW MECHANISMS INVOLVING ENABLES, VALID, STALL, READY SIGNALS

- GENERATE {} MUTATIONS. EACH MUST:
  - INTRODUCE A **SINGLE FUNCTIONAL BUG** THAT CAUSES MISBEHAVIOR, INVALID OUTPUTS, ILLEGAL STATES, OR VIOLATED PROTOCOLS
  - BE STRUCTURAL AND SEMANTICALLY RELEVANT TO THE CODE'S INTENT
  - BELONG TO A CATEGORY DETERMINED BY THE MODULE CONTEXT, DRAWING FROM SUGGESTIONS SUCH AS:
    - **FSM_CORRUPTION_MULTILINE**: Alter state transitions to create dead/unreachable/incorrect states
    - **PIPELINE_HAZARD**: Remove control logic that handles valid/stall/ready signals
    - **TIMING_VIOLATION**: Modify edge sensitivity or remove/reset synchronization
    - **FAULT_INJECTION**: Insert stuck-at faults, invert resets, corrupt outputs
    - OR SIMILAR CATEGORIES AS APPROPRIATE FOR THE CONTEXT

- FOR EACH MUTATION, OUTPUT A **SEPARATE JSON OBJECT** IN AN ARRAY CONTAINING:
  - `"mutation_type"`: A descriptive tag (e.g., `"FSM_CORRUPTION_MULTILINE"`)
  - `"original_code"`: Full, unmodified snippet to match (including indentation and line breaks)
  - `"mutated_code"`: Snippet with exactly one mutation applied (must preserve structure)
  - `"bug_description"`: A one-line explanation of the bug's *functional* impact (e.g., “State EXEC becomes unreachable due to incorrect transition.”)
  - `"fix_comment"`: A one-line fix suggestion (e.g., “Restore transition from LOAD to EXEC on data_ready.”)

- EACH MUTATION MUST BE **INDEPENDENT** (do not reuse or alter overlapping lines or signals) AND **REALISTIC AND SEMANTICALLY RELEVANT**

- THE FORMAT MUST ENABLE STRAIGHTFORWARD STRING MATCHING AND REPLACEMENT IN THE SOURCE FILE — NO LINE NUMBERS OR COMMENTS NEEDED.

- THE `original_code` MUST BE EXACTLY COPY-PASTABLE FROM THE INPUT CODE.

- THE `mutated_code` MUST PRESERVE INDENTATION FOR CLEAN PATCHING.

- ENSURE THAT `original_code` AND `mutated_code` STRINGS ARE ESCAPED PROPERLY (e.g., NEWLINES AS `\\n`, QUOTES AS `\\\"`) TO PRODUCE VALID JSON PARSEABLE BY PYTHON'S `json.loads()`.

- ADDITIONAL REQUIREMENTS: {}
</instructions>

<what not to do>
- NEVER INTRODUCE PERFORMANCE BUGS (E.G., DELAYED SIGNALS, UNOPTIMIZED PATHS)
- NEVER INCLUDE MORE THAN ONE MUTATION PER JSON OBJECT.
- NEVER OVERLAP LINE RANGES OR MUTATE THE SAME LOGIC TWICE.
- NEVER INCLUDE NON-FUNCTIONAL OR MICRO-OPTIMIZATION ERRORS
- NEVER MODIFY SIGNAL NAMES, IDENTIFIERS, OR INTRODUCE SYNTAX ERRORS.
- NEVER OUTPUT EXPLANATIONS, HEADERS, OR ANYTHING OUTSIDE THE JSON ARRAY.
- AVOID TRIVIAL MUTATIONS.
- DO NOT ABSTRACT, SUMMARIZE, OR OMIT LINES FROM `original_code` OR `mutated_code`.
- NEVER ALTER SIGNAL NAMES OR INTRODUCE SYNTAX ERRORS.
</what not to do>

<High Quality Few-Shot Example>
<USER INPUT>
```verilog
always_ff @(posedge clk) begin
  if (rst) begin
    valid <= 0;
    state <= IDLE;
  end else begin
    case (state)
      IDLE: if (start) begin
        data_reg <= in_data;
        state <= LOAD;
      end
      LOAD: begin
        if (data_ready)
          state <= EXEC;
        else
          state <= LOAD;
      end
      EXEC: begin
        result <= data_reg * 4;
        valid <= 1;
        state <= IDLE;
      end
    endcase
  end
end
```
</USER INPUT>

<ASSISTANT RESPONSE>
```json
[
  {{
    "mutation_type": "FSM_CORRUPTION_MULTILINE",
    "original_code": "      LOAD: begin\\n        if (data_ready)\\n          state <= EXEC;\\n        else\\n          state <= LOAD;\\n      end",
    "mutated_code": "      LOAD: begin\\n        if (data_ready)\\n          state <= LOAD;\\n        else\\n          state <= IDLE;\\n      end",
    "bug_description": "State EXEC becomes unreachable, preventing computation stage from ever executing.",
    "fix_comment": "Restore transition to EXEC when data_ready is high."
  }}
]
```
</ASSISTANT RESPONSE>
</High Quality Few-Shot Example>
"""
