# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

PROMPTS = {
    'simple':
        """
        I am creating an exam. Please, add one bug in the provided Verilog code 
        so people can find it during the exam. Make the bug a typical human 
        engineering error. Return an answer in JSON format. The first key must be 
        "updated_code" with the updated buggy code. The second key must be 
        "description" with an extensive description of the proposed bug. 
        Verilog code snippet: \n{}\n
        """,
    'detailed':
        """
        I want you to act as a helpful exam questions creator assistant for Verilog code.\n
        You are preparing exam questions for Verilog code analysis. Modify the 
        following Verilog code snippet by introducing a typical human engineering error. 
        Generate an erroneous code and provide it in JSON format, where the updated_code 
        property is the modified code and the description property is a detailed description 
        of the introduced error.\n
        Verilog code snippet: \n{}\n
        Example Response:\n
        JSON {{ "updated_code": "<modified_code>", "description": "<error_description> }}"\n
        Please generate an erroneous code based on the provided Verilog code snippet and describe. 
        Return only JSON.
        """,
    'code_only': '{}'
}

INSTRUCTIONS = {
    'general':
        """
        - Be highly organized;\n
        - Be proactive and anticipate my needs;\n
        - Mistakes erode my trust, so be accurate and thorough;\n
        - If provided with a block of code always return the updated version of it.
        """,
    'assistant':
        """
        You are a helpful assistant, who will help me implement a bug into a 
        Verilog code snippet provided by me. I am preparing quiz questions for the exam. 
        I want you to implement a human engineering bug, so students can identify them.\n
        \n
        Return result only in JSON format: with properties updated_code (modified code) and 
        description (bug description). Consistency of JSON result is important since I will 
        later upload it on an exam taking platform, which requires JSON. 
        !Important! Return only JSON result, no extra text.
        """,
    'assistant_experimental':
        """
        You are a helpful assistant, who will help me implement a bug into a Verilog code snippet provided by me. 
        I am preparing quiz questions for the exam. I want you to implement a human engineering bug, so students 
        can identify them. 
        
        Return result only in JSON format: with properties original_code (the exact line/lines of code you change, 
        not the whole original code), updated_code (the exact line/lines of a modified code that should replace the 
        original one), line_number (the exact line number of the original code from which you start modifying it) 
        and description (extensive bug description). Consistency of JSON result is important since I will later 
        upload it on an exam taking platform, which requires JSON. 
        
        !Important! Return only JSON result, no extra text. 
        !Important! Return multiple lines of code only if you modify multiple lines of original code or if you add 
        new lines. In any other cases, try to return the exact single line of code.
        """,
    'assistant_experimental_no_description':
        """
        You are a helpful assistant tasked with introducing a specific type of bug into a Verilog code snippet provided by me. 
        These modifications are for creating quiz questions aimed at testing students' ability to identify and understand common 
        pitfalls in Verilog coding. 

        Please introduce a bug that falls into one of the following categories: logical errors, subtle syntax issues that still 
        allow compilation, or race conditions. 

        Return the result exclusively in JSON format, with the following requirements: 
        - The JSON object must contain exactly two properties: `original_code` and `updated_code`. 
        - Both `original_code` and `updated_code` must be strings. 
        - If the modification involves multiple lines or introduces new lines, concatenate them into a single string, using a 
        recognizable delimiter (e.g., `\n`) to maintain readability. 
        - If the modification is limited to a single line of code, include only that line in both the original_code and updated_code strings. 
        - Ensure these modifications are consistent and easily searchable within a code file for replacement purposes. 

        !Important! The JSON response must not include dictionaries, lists, or any non-string data types for the original_code and updated_code values.
        !Important! Only return the JSON result, without extra explanatory text. 
        Example format for clarity:
        {
            "original_code": "Original code snippet here, possibly spanning multiple lines.",
            "updated_code": "Updated code snippet here with the introduced bug, following the same format."
        }
        """
}
