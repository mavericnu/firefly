import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=api_key)

# assistant = client.beta.assistants.create(
#     name="Bug Injector",
#     instructions="",
#     tools=[],
#     model="gpt-4o",
# )

# thread = client.beta.threads.create()

# message = client.beta.threads.messages.create(
#     thread_id=thread.id,
#     role="user",
#     content="",
# )

# run = client.beta.threads.runs.create(
#     thread_id=thread.id,
#     assistant_id=assistant.id,
#     instructions="",
# )

# while run.status in ["queued", "in_progress"]:
#     keep_retrieving_run = client.beta.threads.runs.retrieve(
#         thread_id=thread.id,
#         run_id=run.id,
#     )

#     if keep_retrieving_run.status == "completed":
#         all_messages = client.beta.threads.messages.list(
#             thread_id=thread.id
#         )

#         print(f"User: {message.content[0].text.value}")
#         print(f"Assistant: {all_messages.data[0].content[0].text.value}")

#         break

#     elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
#         pass

#     else:
#         print(f"Run status: {keep_retrieving_run.status}")
#         break

  
assistant = client.beta.assistants.create(
  name="Math Tutor",
  instructions="You are a personal math tutor. Write and run code to answer math questions.",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4o",
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)

from typing_extensions import override
from openai import AssistantEventHandler
 
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.
 
class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)
 
# Then, we use the `stream` SDK helper 
# with the `EventHandler` class to create the Run 
# and stream the response.
 
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account.",
  event_handler=EventHandler(),
) as stream:
  stream.until_done()