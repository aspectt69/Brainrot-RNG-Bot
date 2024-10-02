import discord
from discord.ext import commands
import asyncio
import sqlite3
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import logging

load_dotenv()

encryption_key = os.getenv('ENCRYPTION_KEY')
bot_token = os.getenv('BOT_TOKEN')

if not all([[bot_token, encryption_key]]):
    raise ValueError("One or more required environment variables are missing.")

logging.basicConfig(level=logging.DEBUG)
cipher = Fernet(encryption_key.encode())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready(): 
    logging.debug(f"{bot.user} is ready")

bot.run(bot_token)