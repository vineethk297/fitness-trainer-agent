from dotenv import load_dotenv
import json
import data as d
import judge as jd
# import judge_verdicts as jv
import anthropic
load_dotenv()

client = anthropic.Anthropic()

with open("system_prompt.txt","r") as f:
    system_prompt = f.read()
    

with open("judge_verdicts.json", "r") as f:
    verdicts = json.load(f)

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
trials_per_profile = 5
for trial in range(trials_per_profile):
    # for i in range(count):
    i = 2
    # print("\n")
    # print(f"For User_{i+1}:\n")
    test_case = d.test_cases[i]
    response = run_profile(test_case, system_prompt, client)
    # print(response)
    
    # print("\n")
    # print(f"Judge Response For User_{i+1}:\n")
    judge_response = jd.judge_response(test_case, response["intake_reply"], response["final_plan"], client)
    verdicts[f"user_{i+1}"].append(judge_response)
    print(f"trial {trial+1}/{trials_per_profile} — user_{i+1} done")
    with open("judge_verdicts.json", "w") as f:
        json.dump(verdicts, f, indent=2)


