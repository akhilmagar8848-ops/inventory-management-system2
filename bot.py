import os
import discord
from groq import Groq

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

INPUT_CHANNEL_ID = 123456789012345678   # #project-input ko 18-digit Channel ID halnu hos
PLAN_CHANNEL_ID = 1573568221775396916    # #manager-plan ko ID

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
groq_client = Groq(api_key=GROQ_API_KEY)


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

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sharp project manager. Turn incoming requests "
                    "into clear action steps, tasks, and milestones."
                ),
            },
            {
                "role": "user",
                "content": message.content,
            },
        ],
    )

    plan_text = response.choices[0].message.content or "Could not generate a plan."

    for start in range(0, len(plan_text), 1900):
        await plan_channel.send(plan_text[start : start + 1900])


client.run(DISCORD_TOKEN)

