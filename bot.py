import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import os
from datetime import datetime
from pytz import timezone

# Set timezone to Eastern for MLB
ET = timezone('US/Eastern')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Config - change these
HR_CHANNEL_ID = 0  # Replace with your channel ID
TEAM_ID = 121  # 121 = Mets. Change to your team: 147=Yankees, 119=LA Dodgers, etc

# Team name lookup
TEAM_NAMES = {
    121: "Mets", 147: "Yankees", 119: "Dodgers", 133: "Athletics",
    134: "Pirates", 135: "Padres", 136: "Mariners", 137: "Giants",
    138: "Cardinals", 139: "Rays", 140: "Rangers", 141: "Blue Jays",
    142: "Twins", 143: "Phillies", 144: "Braves",
