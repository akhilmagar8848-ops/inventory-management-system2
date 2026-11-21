import json
import os
import urllib.request
import discord

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

INPUT_CHANNEL_ID = 123456789012345678
PLAN_CHANNEL_ID = 1573568221775396916

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def ask_groq(prompt_text: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a sharp project manager. Turn incoming requests "
                    "into clear action steps, tasks, and milestones."
                ),
            },
            {
                "role": "user",
                "content": prompt_text,
            },
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != INPUT_CHANNEL_ID:
        return

    plan_channel = client.get_channel(PLAN_CHANNEL_ID)
    if plan_channel is None:
        return

    try:
        plan_text = ask_groq(message.content) or "Could not generate a plan."
    except Exception as e:
        plan_text = f"Groq API error: {e}"

    for start in range(0, len(plan_text), 1900):
        await plan_channel.send(plan_text[start : start + 1900])


client.run(DISCORD_TOKEN)
