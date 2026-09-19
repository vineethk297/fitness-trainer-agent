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
    
# count = len(d.test_cases)
# trials_per_profile = 5
# for trial in range(trials_per_profile):
#     for i in range(count):
#         # print("\n")
#         # print(f"For User_{i+1}:\n")
#         test_case = d.test_cases[i]
#         response = run_profile(test_case, system_prompt, client)
#         # print(response)
        
#         # print("\n")
#         # print(f"Judge Response For User_{i+1}:\n")
#         judge_response = jd.judge_response(test_case, response["intake_reply"], response["final_plan"], client)
#         verdicts[f"user_{i+1}"].append(judge_response)
#         print(f"trial {trial+1}/{trials_per_profile} — user_{i+1} done")
#         with open("judge_verdicts.json", "w") as f:
#             json.dump(verdicts, f, indent=2)

def parse_verdict(verdict_txt):
    result = {"criteria" : {}, "overall" : None}
    lines = verdict_txt.split("\n")
    for line in lines:
        if not line.strip():
            continue  # skip blank lines
        tx = line.split(":")
        if tx[0].strip() == "OVERALL":
            result["overall"] = tx[1].strip()
        elif tx[0].strip().startswith("CRITERION") and len(tx) > 1:
            criterion = tx[0].split()
            verdict = tx[1].split("-")[0].strip()
            result["criteria"][int(criterion[1])] = verdict
    print(result)
    return result
        
# verdict_1 = verdicts["user_1"][0]
parsed_results = {}
for profile_id, verdicts_list in verdicts.items():
    parsed_results[profile_id] = [parse_verdict(v) for v in verdicts_list]
# print(parsed_results)


print(compute_pass_rates(parsed_results))def compute_pass_rates(parsed_results):
    summary = {}
    for profile_id, trials in parsed_results.items():
        total = len(trials)
        overall_passes = sum(1 for t in trials if t["overall"] == "PASS")
        
        criterion_passes = {}
        criterion_numbers = trials[0]["criteria"].keys()  

        for crit_num in criterion_numbers:
            count = 0
            for t in trials:
                if t["criteria"].get(crit_num) == "PASS":
                    count += 1
            criterion_passes[f"criterion_{crit_num}"] = f"{count}/{total}"
        summary[profile_id] = {
            "overall_pass_rate": f"{overall_passes}/{total}",
            "criterion_pass_rates": criterion_passes
        }
    return summary