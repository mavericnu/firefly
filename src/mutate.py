# Copyright (c) 2025 Maveric @ NU and Texer.ai. All rights reserved.
import google.generativeai as genai
import json
import re
import time

from collections import deque
from src.constants import RATE_LIMIT, TIME_WINDOW, MAX_RETRIES, PROMPT


# Set up API client.
genai.configure()
gemini = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")


# Define all functions.
def read_file(file_path, read_mode="r"):
    with open(file_path, "r") as f:
        return f.readlines() if read_mode == "rl" else f.read()


def read_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def transform_response(response):
    pattern = r"```(?:json)?\s*([\s\S]*?)```"
    match = re.search(pattern, response)
    json_str = match.group(1).strip()
    return json_str


def validate_mutations(file_path, mutations):
    valid_mutations = []
    file_content = read_file(file_path)
    for mutation in mutations:
        original_code = mutation["original_code"]
        if original_code in file_content:
            valid_mutations.append(mutation)
        else:
            raise ValueError(
                f"Could not locate the original code in the source file for {mutation}"
            )
    return valid_mutations


def prompt_model(content):
    response = gemini.generate_content(content).text
    # Remove markdown-style backticks.
    if "```json" in response:
        response = transform_response(response)
    data = json.loads(response)
    return data


request_timestamps = deque()


def _generate_mutations_batch(tasks_to_process, mutations):
    failed_tasks = []
    global request_timestamps

    for file_path, mutations_to_request in tasks_to_process:
        current_time = time.time()
        while (
            request_timestamps and request_timestamps[0] <= current_time - TIME_WINDOW
        ):
            request_timestamps.popleft()
        if len(request_timestamps) >= RATE_LIMIT:
            time_since_oldest_allowed = current_time - request_timestamps[0]
            wait_time = max(0, TIME_WINDOW - time_since_oldest_allowed)
            if wait_time > 0:
                print(f"  -- Rate limit reached. Sleeping for {wait_time:.2f} seconds.")
                time.sleep(wait_time)
            current_time = time.time()
            while (
                request_timestamps
                and request_timestamps[0] <= current_time - TIME_WINDOW
            ):
                request_timestamps.popleft()

        request_timestamps.append(time.time())

        try:
            print(
                f"-- Attempting: {file_path}, requesting {mutations_to_request} mutations."
            )
            file_content = read_file(file_path)
            prompt = PROMPT.format(
                file_path.split("/")[-1], file_content, mutations_to_request
            )
            file_mutations_result = prompt_model(prompt)
            validated_result = validate_mutations(file_path, file_mutations_result)
            mutations[file_path] = validated_result
        except FileNotFoundError:
            print(f"  -- Failure (File Not Found): {file_path}.")
        except ValueError as ve:
            print(
                f"  -- Failure (Validation): {file_path}, Error: {ve}. Will retry if possible."
            )
            failed_tasks.append((file_path, mutations_to_request))
        except json.JSONDecodeError as jde:
            print(
                f"  -- Failure (JSON Parsing): {file_path}, Error: {jde}. Will retry if possible."
            )
            failed_tasks.append((file_path, mutations_to_request))
        except Exception as e:
            print(
                f"  -- Failure (Other): {file_path}, Error: {e}. Will retry if possible."
            )
            failed_tasks.append((file_path, mutations_to_request))

    return failed_tasks


def spawn_mutations():
    config = read_json("config.json")
    target_files = config["target_files"]
    num_mutations = int(config["num_mutations"])
    files_count = len(target_files)
    mutations = {}

    initial_tasks = []
    if files_count == 0:
        print("-- No target files specified.")
        return False

    if files_count < num_mutations:
        mutations_per_file = num_mutations // files_count
        remaining_mutations = num_mutations % files_count
        for i, file_path in enumerate(target_files):
            file_mutations_count = mutations_per_file
            if i < remaining_mutations:
                file_mutations_count += 1
            if file_mutations_count > 0:
                initial_tasks.append((file_path, file_mutations_count))
    else:
        selected_files = target_files[:num_mutations]
        for file_path in selected_files:
            initial_tasks.append((file_path, 1))

    tasks_to_process = initial_tasks
    retries = 0
    while tasks_to_process and retries <= MAX_RETRIES:
        if retries > 0:
            print(
                f"\n-- Retry Attempt {retries}/{MAX_RETRIES} for {len(tasks_to_process)} failed tasks."
            )
        else:
            print(f"-- Starting initial processing for {len(tasks_to_process)} tasks.")

        failed_tasks = _generate_mutations_batch(tasks_to_process, mutations)
        tasks_to_process = failed_tasks
        retries += 1

    if tasks_to_process:
        print(
            f"\n-- Warning: {len(tasks_to_process)} tasks failed after {MAX_RETRIES} retries."
        )
        for f_path, _ in tasks_to_process:
            print(f"  -- Final failure: {f_path}")
    else:
        print("\n-- All tasks completed successfully.")

    print("-- Writing results to mutations.json...")
    with open("mutations.json", "w") as json_file:
        json.dump(mutations, json_file, indent=4)
    return not bool(tasks_to_process)
