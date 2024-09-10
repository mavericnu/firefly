# Copyright (c) 2024 Maveric @ NU and Texer.ai.
# All rights reserved.

import re
import os

# -----MAIN FUNCTIONS-----
selected_module_names = set([]) # global variable that stores final module names list that meet criteria
final_paths_list = set([]) #global variable that stores final paths list

def extract_module_types(content):
    pattern = r"([a-zA-Z0-9_]+)\s*#\s*\("
    matches = re.findall(pattern, content.decode('utf-8'), re.DOTALL)
    if matches:
        return matches
    else:
        return None

def extract_file_path_from_root(design_path, module_name):
    modified_string = "module " + module_name + " #("
    folder = os.walk(design_path)
    
    for (dirpath, dirnames, filenames) in folder:
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            
            if (os.path.isfile(file_path) & os.path.exists(file_path)):
                with open(file_path, 'rb') as file:
                        file_content = file.read()
                        if modified_string.encode() in file_content:
                            final_paths_list.add(file_path)

def search_module_names_in_files(design_path, needed_string):
    modified_string = ") " + needed_string + " ("
    folder = os.walk(design_path)
    
    for (dirpath, dirnames, filenames) in folder: #parsing all files in desing of the semiconductor
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            
            if (os.path.isfile(file_path) & os.path.exists(file_path)): #checking either such directory exits
                with open(file_path, 'rb') as file:
                        file_content = file.read()
                        if modified_string.encode() in file_content:
                            result = extract_module_types(file_content)
                            if result:
                                for res in result:
                                    selected_module_names.add(res)
         
def vcd_modules_parse(file_path, design_path, result_file_path):
    
    module_names_from_vcd_file = set([]) #extract module_names from vcd file
    with open(file_path, 'r') as file: 
        file_content = file.read()
        module_names = re.findall(r'\$scope module (\w+) \$end', file_content)
        for module_name in module_names:
            module_names_from_vcd_file.add(module_name)
    
    for module_name in module_names_from_vcd_file:
        search_module_names_in_files(design_path, module_name) #extract module_types from design based on module_names
    
    for line in selected_module_names:
        extract_file_path_from_root(design_path, line) # extract module_declaration's path based on module_types
        
    with open(result_file_path, 'w') as module_paths_list_file: # save results
        for line in final_paths_list:
            module_paths_list_file.write(line + '\n')

vcd_modules_parse('hello_world.cv32a60x.vcd', './cva6', 'module_paths.txt')

# -----INTERMEDIATE FUNCTIONS (not involved in final script)-----

def extract_closest_declaration(content, target_variable):
    pattern = r'(\w+)\s*#\(([^)]+)\)\s*\w+\s*\('
    
    matches = list(re.finditer(pattern, content.decode('utf-8')))
    print(matches)
    instance_pattern = re.compile(r'\b' + re.escape(target_variable) + r'\b')

    target_match = instance_pattern.search(content.decode('utf-8'))
    
    if not target_match:
        return None  # No instance of the target variable found

    target_position = target_match.start()

    # Find the closest declaration preceding the target variable instance
    closest_declaration = None
    for match in matches:
        if match.start() < target_position:
            closest_declaration = match
        else:
            break

    if closest_declaration:
        module_name = closest_declaration.group(1)
        parameters = closest_declaration.group(2)
        return module_name, parameters
    else:
        return None

def save_vcd_modules_in_file(file_path, result_path):
    result_arr = set([])
    with open(file_path, 'r') as file: 
        content = file.read()
        module_names = re.findall(r'\$scope module (\w+) \$end', content)
        for module_name in module_names:
            result_arr.add(module_name)
    
    with open(result_path, 'w') as result_file:
        for line in result_arr:
            result_file.write(line + '\n')
    
def search_module_declaration(folder_path, needed_string):
    modified_string = "module " + needed_string
    folder = os.walk(folder_path)
    for (dirpath, dirnames, filenames) in folder:   
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            if (os.path.isfile(file_path) & os.path.exists(file_path)):
                with open(file_path, 'rb') as temp_file:
                        content = temp_file.read()
                        if modified_string.encode() in content:
                            # result = extract_closest_declaration(content, needed_string)

                            # if result:
                            #     module_name, params = result
                            #     print(f"Module Name: {module_name}")
                            #     print(f"Parameters: {params}")
                            # else:
                            #     print("No matching declaration found closest to the target variable")
                            result = extract_string_before_hash(content)
                            if result:
                                selected_module_names.add(result)

def extract_string_before_hash(content): #this function can be improved
    pattern = r'(\w+)\s*#\(([^)]+)\)'    
    matches = re.findall(pattern, content.decode('utf-8'))
    if matches:
        variable_name, content_before_hash = matches[0]
        return variable_name
    else:
        return None

# -----TESTING FEILD------
content = """// Copyright 2018 ETH Zurich and University of Bologna.
//
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Fabian Schuiki <fschuiki@iis.ee.ethz.ch>

/// A two-phase clock domain crossing.
///
/// CONSTRAINT: Requires max_delay of min_period(src_clk_i, dst_clk_i) through
/// the paths async_req, async_ack, async_data.
/* verilator lint_off DECLFILENAME */
module cdc_2phase #(
  parameter type T = logic
)(
  input  logic src_rst_ni,
  input  logic src_clk_i,
  input  T     src_data_i,
  input  logic src_valid_i,
  output logic src_ready_o,

  input  logic dst_rst_ni,
  input  logic dst_clk_i,
  output T     dst_data_o,
  output logic dst_valid_o,
  input  logic dst_ready_i
);

  // Asynchronous handshake signals.
  (* dont_touch = "true" *) logic async_req;
  (* dont_touch = "true" *) logic async_ack;
  (* dont_touch = "true" *) T async_data;

  // The sender in the source domain.
  cdc_2phase_src #(.T(T)) i_src (
    .rst_ni       ( src_rst_ni  ),
    .clk_i        ( src_clk_i   ),
    .data_i       ( src_data_i  ),
    .valid_i      ( src_valid_i ),
    .ready_o      ( src_ready_o ),
    .async_req_o  ( async_req   ),
    .async_ack_i  ( async_ack   ),
    .async_data_o ( async_data  )
  );

  // The receiver in the destination domain.
  cdc_2phase_dst #(.T(T)) i_dst (
    .rst_ni       ( dst_rst_ni  ),
    .clk_i        ( dst_clk_i   ),
    .data_o       ( dst_data_o  ),
    .valid_o      ( dst_valid_o ),
    .ready_i      ( dst_ready_i ),
    .async_req_i  ( async_req   ),
    .async_ack_o  ( async_ack   ),
    .async_data_i ( async_data  )
  );

endmodule


/// Half of the two-phase clock domain crossing located in the source domain.
module cdc_2phase_src #(
  parameter type T = logic
)(
  input  logic rst_ni,
  input  logic clk_i,
  input  T     data_i,
  input  logic valid_i,
  output logic ready_o,
  output logic async_req_o,
  input  logic async_ack_i,
  output T     async_data_o
);

  (* dont_touch = "true" *)
  logic req_src_q, ack_src_q, ack_q;
  (* dont_touch = "true" *)
  T data_src_q;

  // The req_src and data_src registers change when a new data item is accepted.
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      req_src_q  <= 0;
      data_src_q <= '0;
    end else if (valid_i && ready_o) begin
      req_src_q  <= ~req_src_q;
      data_src_q <= data_i;
    end
  end

  // The ack_src and ack registers act as synchronization stages.
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      ack_src_q <= 0;
      ack_q     <= 0;
    end else begin
      ack_src_q <= async_ack_i;
      ack_q     <= ack_src_q;
    end
  end

  // Output assignments.
  assign ready_o = (req_src_q == ack_q);
  assign async_req_o = req_src_q;
  assign async_data_o = data_src_q;

endmodule"""

