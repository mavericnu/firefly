# Copyright (c) 2024 Maveric @ NU and Texer.ai. All rights reserved.
import json
import sys
import tiktoken
import time

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

role = ""
prompt = ""
token_limit = 100000

