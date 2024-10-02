import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import sqlite3
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import logging

load_dotenv()

encryption_key = os.getenv('ENCRYPTION_KEY')
bot_token = os.getenv('TOKEN')
guild = discord.Object(id=1150387912471490700)

if not all([[bot_token, encryption_key]]):
    raise ValueError("One or more required environment variables are missing.")

logging.basicConfig(level=logging.DEBUG)
cipher = Fernet(encryption_key.encode())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Classes
class BrainRot():

    def __init__(self, name, rarity, percentage):
        self.name = name
        self.rarity = rarity
        self.percentage = percentage

class Boost():

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return self.name
    
#Defining the different items you can roll
sigma = BrainRot("Sigma", "common",  "54%")
skibidi = BrainRot("Skibidi", "rare", "25%")
oioioi = BrainRot("Oi Oi Oi!", "legendary", "10%")
johnpork = BrainRot("John Pork!", "mythic", "5%")
freakbob = BrainRot("FREAKBOB??", "mythic", "5%")
rizz = BrainRot("Rizz", "godly", "1%")

#Defining the different boosts
luckboost1 = Boost("Luck-Boost1", 15)
luckboost2 = Boost("Luck-Boost2", 30)
multiroll1 = Boost("Multi-Roll1", 20)
multiroll2 = Boost("Multi-Roll2", 40)

@bot.event
async def on_ready(): 
    logging.debug(f"{bot.user} is ready")
    try:
        synced = await bot.tree.sync()
        logging.debug(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.debug(e)

@bot.tree.command(name="start")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(f"Started {interaction.user.mention}", ephemeral=True)

@bot.tree.command(name="say")
@app_commands.describe(arg = "What should i say?")
async def say(interaction: discord.Interaction, arg: str):
    await interaction.response.send_message(f"{interaction.user.name} said: '{arg}'")

bot.run(bot_token)