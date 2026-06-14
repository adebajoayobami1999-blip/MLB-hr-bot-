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
HR_CHANNEL_ID = 0 # Replace with your channel ID
TEAM_ID = 121 # 121 = Mets. Change to your team: 147=Yankees, 119=LA Dodgers, etc

# Team name lookup
TEAM_NAMES = {
    121: "Mets", 147: "Yankees", 119: "Dodgers", 133: "Athletics",
    134: "Pirates", 135: "Padres", 136: "Mariners", 137: "Giants",
    138: "Cardinals", 139: "Rays", 140: "Rangers", 141: "Blue Jays",
    142: "Twins", 143: "Phillies", 144: "Braves", 145: "White Sox",
    146: "Tigers", 148: "Guardians", 149: "Reds", 150: "Rockies",
    151: "Nationals", 152: "Astros", 153: "Angels", 154: "Diamondbacks",
    155: "Orioles", 156: "Royals", 158: "Brewers", 159: "Red Sox",
    160: "Marlins", 161: "Cubs", 162: "Cleveland", 171: "Blue Jays"
}

seen_hrs = set()

async def check_hrs():
    async with aiohttp.ClientSession() as session:
        # Get today's games for your team
        today = datetime.now(ET).strftime("%Y-%m-%d")
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}&teamId={TEAM_ID}"
        
        async with session.get(url) as r:
            data = await r.json()
            
        if not data.get("dates") or not data["dates"][0].get("games"):
            return
            
        for game in data["dates"][0]["games"]:
            game_pk = game["gamePk"]
            
            # Get live feed for this game
            async with session.get(f"https://statsapi.mlb.com/api/v1/game/{game_pk}/feed/live") as r:
                game_data = await r.json()
            
            # Check all plays for home runs
            plays = game_data.get("liveData", {}).get("plays", {}).get("allPlays", [])
            
            for play in plays:
                result = play.get("result", {})
                async with session.get(f"https://statsapi.mlb.com/api/v1/game/{game_pk}/feed/live") as r:
                    play_id = play.get("about", {}).get("atBatIndex", "")
                    
                    if play_id not in seen_hrs:
                        seen_hrs.add(play_id)
                        
                        batter = play.get("matchup", {}).get("batter", {}).get("fullName", "Unknown")
                        team = play.get("about", {}).get("halfInning", "")
                        inning = play.get("about", {}).get("inning", "")
                        
                        # Get pitch speed if available
                        pitch_speed = ""
                        pitches = play.get("playEvents", [])
                        if pitches:
                            last_pitch = pitches[-1].get("playSpeed", "")
                            if last_pitch:
                                pitch_speed = f" | {last_pitch} mph"
                        
                        team_name = TEAM_NAMES.get(TEAM_ID, "Your Team")
                        msg = f"HR ALERT: {batter} just went yard for the {team_name}! {team} {inning}{pitch_speed}"
                        
                        channel = bot.get_channel(HR_CHANNEL_ID)
                        if channel:
                            await channel.send(msg)

@tasks.loop(seconds=30)
async def hr_checker():
    try:
        await check_hrs()
    except Exception as e:
        print(f"Error checking HRs: {e}")

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    hr_checker.start()

bot.run(os.getenv('DISCORD_TOKEN'))
