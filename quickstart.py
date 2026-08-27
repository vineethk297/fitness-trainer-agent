from dotenv import load_dotenv
import anthropic
load_dotenv()

client = anthropic.Anthropic()

with open("system_prompt.txt","r") as f:
    system_prompt = f.read()
    
with open("user_1.txt","r") as u1:
    user_1 = u1.read()

messages = [
        {
            "role":"user",
            "content":user_1
        }
    ]

message = client.messages.create(
    model ="claude-opus-5",
    max_tokens=1000,
    system=system_prompt,
    messages=messages
)

response_1 = None
print(response_1)
for block in message.content:
    if block.type=="text":
        response_1 = block.text
        print(response_1)

messages.append({"role":"assistant", "content":response_1})

follow_up_answers = """
1. It mostly eases up once I stand and walk around for a few minutes — hasn't traveled into my hip or leg, just stays in the lower back.
2. True fresh start — I played some sports in high school but nothing consistent since college.
3. Getting about 6-7 hours, honestly inconsistent. I feel most alert mid-morning, pretty foggy by late afternoon.
4. I have a long loop resistance band and a mini glute band. I've got floor space in my living room and a sturdy dining chair.
"""

messages.append({"role":"user", "content":follow_up_answers})

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1500,
    system=system_prompt,
    messages=messages
)

response_2 = None
print(response_2)
for block in message.content:
    if block.type=="text":
        response_2 = block.text
        print(response_2)
