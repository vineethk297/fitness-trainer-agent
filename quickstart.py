from dotenv import load_dotenv
import data as d
import anthropic
load_dotenv()

client = anthropic.Anthropic()

with open("system_prompt.txt","r") as f:
    system_prompt = f.read()

def run_profile(test_case, system_prompt, client):
    messages = []
    messages.append({"role":"user", "content":test_case["initial_message"]})
    
    response_1 = client.messages.create(
        model ="claude-opus-5",
        max_tokens=1000,
        system=system_prompt,
        messages=messages
    )
    
    intake_reply = None
    for block in response_1.content:
        if block.type=="text":
            intake_reply = block.text
            print(intake_reply)
    
    messages.append({"role":"assistant", "content":intake_reply})
    
    messages.append({"role":"user", "content":test_case["follow_up_answers"]})
    
    response_2  = client.messages.create(
        model="claude-opus-5",
        max_tokens=2500,
        system=system_prompt,
        messages=messages
    )
    
    final_plan = None
    for block in response_2.content:
        if block.type=="text":
            final_plan = block.text
            print(final_plan)

    return {
        "profile_id" : test_case["profile_id"],
        "intake_reply" : intake_reply,
        "final_plan" : final_plan
    }
    
count = len(d.test_cases)
for i in range(count):
    print(f"For User_{i+1}:\n")
    test_case = d.test_cases[i]
    response = run_profile(test_case, system_prompt, client)
    print(response)