import discord
from discord.ext import commands, tasks
import aiohttp
import os
import datetime
from pytesseract import image_to_string
from PIL import Image
import io
import re

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SGP_CHANNEL = "sgp-picks"
ALERT_CHANNEL = "mlb-alert"
posted_hr = set()

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    hr_alert.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.name == SGP_CHANNEL and message.attachments:
        for att in message.attachments:
            if att.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                data = await att.read()
                img = Image.open(io.BytesIO(data))
                text = image_to_string(img)
                formatted = format_sgp(text)
                if formatted:
                    await message.channel.send(formatted)
    await bot.process_commands(message)

def format_sgp(text):
    picks = []
    lines = text.split('\n')
    for line in lines:
        if re.search(r'\d+(\.\d+)?\s*x', line, re.I):
            picks.append(f"- {line.strip()}")
    if picks:
        return "**SGP Breakdown:**\n" + "\n".join(picks)
    return None

@tasks.loop(seconds=30)
async def hr_alert():
    now = datetime.datetime.utcnow()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=" + now.strftime("%Y-%m-%d")) as r:
            if r.status!= 200:
                return
            data = await r.json()
        for game in data.get('dates', [{}])[0].get('games', []):
            game_pk = game['gamePk']
            async with session.get(f"https://statsapi.mlb.com/api/v1/game
