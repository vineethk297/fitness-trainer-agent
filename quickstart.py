from dotenv import load_dotenv
import anthropic
load_dotenv()

client = anthropic.Anthropic()

with open("system_prompt.txt","r") as f:
    system_prompt = f.read()
    
with open("user_4.txt","r") as u1:
    user_1 = u1.read()

message = client.messages.create(
    model ="claude-opus-5",
    max_tokens=1000,
    system=system_prompt,
    messages=[
        {
            "role":"user",
            "content":user_1
        }
    ]
)

for block in message.content:
    if block.type=="text":
        print(block.text)