from dotenv import load_dotenv
import anthropic
import memory_store as ms
import json as json_module

load_dotenv()
client = anthropic.Anthropic()

with open("system_prompt.txt", "r") as f:
    system_prompt = f.read()

user_id = "vineeth"

existing_memory = ms.load_memory(user_id)
messages = []

if existing_memory is None:
    print("Coach: Hi! I don't have any history for you yet — let's start fresh.")
    user_input = input("You: ")
    messages.append({"role": "user", "content": user_input})
else:
    context_summary = f"""[Returning client — here's what you already know, don't re-ask intake questions unless something seems outdated:]
Profile: {existing_memory['profile']}
Last plan given: {existing_memory['current_plan']}
Recent sessions: {existing_memory['session_log'][-3:]}

Greet them back warmly and ask how recent sessions went."""
    messages.append({"role": "user", "content": context_summary})

while True:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        system=system_prompt,
        messages=messages
    )

    reply = None
    for block in response.content:
        if block.type == "text":
            reply = block.text

    print(f"\nCoach: {reply}\n")
    messages.append({"role": "assistant", "content": reply})

    user_input = input("You (or 'quit' to end): ")
    if user_input.lower() == "quit":
        break
    messages.append({"role": "user", "content": user_input})

# <<< NEW CODE STARTS HERE — replaces your old save block >>>

extraction_prompt = f"""Based on this conversation, extract the client's profile as JSON with these exact keys: age, goal, equipment, injuries_notes, schedule. Use null for anything not mentioned. Return ONLY the JSON, nothing else.

Conversation:
{messages}"""

extraction_response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=500,
    messages=[{"role": "user", "content": extraction_prompt}]
)

profile_json_text = None
for block in extraction_response.content:
    if block.type == "text":
        profile_json_text = block.text

import json as json_module
try:
    extracted_profile = json_module.loads(profile_json_text)
except json_module.JSONDecodeError:
    extracted_profile = existing_memory["profile"] if existing_memory else ms.new_user_template()["profile"]

updated_memory = existing_memory or ms.new_user_template()
updated_memory["profile"] = extracted_profile
updated_memory["current_plan"] = reply
ms.save_memory(user_id, updated_memory)
print("\n(Session saved.)")

extraction_prompt = f"""Based on this conversation, extract the client's profile as JSON with these exact keys: age, goal, equipment, injuries_notes, schedule. Use null for anything not mentioned. Return ONLY the JSON, nothing else.

Conversation:
{messages}"""

extraction_response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=500,
    messages=[{"role": "user", "content": extraction_prompt}]
)

profile_json_text = None
for block in extraction_response.content:
    if block.type == "text":
        profile_json_text = block.text

try:
    extracted_profile = json_module.loads(profile_json_text)
except json_module.JSONDecodeError:
    extracted_profile = existing_memory["profile"] if existing_memory else ms.new_user_template()["profile"]

updated_memory = existing_memory or ms.new_user_template()
updated_memory["profile"] = extracted_profile
updated_memory["current_plan"] = reply
ms.save_memory(user_id, updated_memory)