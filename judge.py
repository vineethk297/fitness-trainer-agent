def build_judge_prompt(test_case, intake_reply, final_plan):
    criteria_list = "\n".join(f"{i+1}. {c}" for i, c in enumerate(test_case["pass_criteria"]))

    return f"""You are a strict evaluator reviewing an AI fitness coach's response for a specific test profile.

PROFILE CONTEXT:
{test_case["initial_message"]}

PASS CRITERIA (evaluate each one independently):
{criteria_list}

FULL CONVERSATION TO EVALUATE (intake response, then the final plan after follow-up answers):
--- INTAKE RESPONSE ---
{intake_reply}

--- FINAL PLAN ---
{final_plan}

INSTRUCTIONS:
- Evaluate each criterion using evidence from EITHER the intake response OR the final plan — a criterion met in the intake still counts as met.
- Be strict: only mark PASS if there is clear, specific evidence in the text. Do not give credit for vague or implied matches.
- For subjective criteria (e.g. "avoids filler text", "maintains an encouraging tone"), judge based on whether the text is reasonably concise/appropriately toned relative to a professional coaching response — not perfection.
- Output ONLY in this exact format, one line per criterion, then an overall line. No preamble, no extra commentary.

CRITERION 1: PASS or FAIL - one sentence reason
CRITERION 2: PASS or FAIL - one sentence reason
(continue for all criteria)
OVERALL: PASS if ALL criteria passed, FAIL if ANY criterion failed
"""


def judge_response(test_case, intake_reply, final_plan, client):
    prompt = build_judge_prompt(test_case, intake_reply, final_plan)

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    for block in response.content:
        if block.type == "text":
            return block.text
    return None