import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def status(ctx):
    response = requests.get("http://localhost:5000/api/status")
    if response.status_code == 200:
        data = response.json()
        await ctx.send(f"Stags: {len(data['stags'])} active")
    else:
        await ctx.send("Failed to fetch status")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))