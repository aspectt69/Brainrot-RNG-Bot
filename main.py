import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import sqlite3
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import logging
import random

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
bot = commands.Bot(command_prefix='_', intents=intents)

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

brainrots = [sigma, skibidi, oioioi, johnpork, freakbob, rizz]

#Defining the different boosts
luckboost1 = Boost("Luck-Boost1", 15)
luckboost2 = Boost("Luck-Boost2", 30)
multiroll1 = Boost("Multi-Roll1", 20)
multiroll2 = Boost("Multi-Roll2", 40)

connection = sqlite3.connect('brainrot_rng.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS player_data (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS player_brainrots (
    user_id INTEGER,
    brainrot_name TEXT,
    amount INTEGER,
    PRIMARY KEY (user_id, brainrot_name)
)
''')
connection.commit()

def check_start_status():
    pass

@bot.event
async def on_ready(): 
    logging.debug(f"{bot.user} is ready")
    try:
        synced = await bot.tree.sync()
        logging.debug(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.debug(e)

@bot.tree.command(name="start", description="Use this command to begin playing")
async def start(interaction: discord.Interaction):
    cursor.execute('SELECT * FROM player_data WHERE user_id = ?', (interaction.user.id,))
    result = cursor.fetchone()
    if result:
        await interaction.response.send_message(f"{interaction.user.mention}, you've already started!")
        logging.debug(f"{interaction.user} is already in the database (id:{interaction.user.id})")
    else:
        try:
            cursor.execute('INSERT INTO player_data (user_id, coins) VALUES (?, ?)', (interaction.user.id, 0,))
            connection.commit()
            await interaction.response.send_message(f"Successfully started, {interaction.user.mention}!")
            logging.debug(f"Successfully added {interaction.user} into the database (id:{interaction.user.id})")
        except:
            await interaction.response.send_message(f"Sorry, there was an error, maybe try again?")
            logging.debug(f"Couldn't start for {interaction.user} (id:{interaction.user.id})")

@bot.tree.command(name="roll", description="Use this command to roll")
async def roll(interaction: discord.Interaction):
    sigma.percentage = "54%"
    skibidi.percentage = "25%"
    oioioi.percentage = "10%"
    johnpork.percentage = "5%"
    freakbob.percentage = "5%"
    rizz.percentage = "1%"
    
    chances = 54,25,10,5,5,1

    rolleditem = random.choices(brainrots, weights=(chances), k=1)[0]

    match rolleditem.name:
        case sigma.name:
            coinsgained = 1
        case skibidi.name:
            coinsgained = 2
        case oioioi.name:
            coinsgained = 3
        case johnpork.name:
            coinsgained = 5
        case freakbob.name:
            coinsgained = 5
        case rizz.name:
            coinsgained = 10

    cursor.execute('SELECT amount FROM player_brainrots WHERE user_id = ? AND brainrot_name = ?', (interaction.user.id, rolleditem.name,))
    result = cursor.fetchone()
    if result:
        new_amount = result[0] + 1
        cursor.execute('UPDATE player_brainrots SET amount = ? WHERE user_id = ? AND brainrot_name = ?', (new_amount, interaction.user.id, rolleditem.name,))
    else:
        cursor.execute('INSERT INTO player_brainrots (user_id, brainrot_name, amount) VALUES (?, ?, ?)', (interaction.user.id, rolleditem.name, 1,))
    connection.commit()
    cursor.execute('SELECT coins FROM player_data WHERE user_id = ?', (interaction.user.id,))
    coins_result = cursor.fetchone()
    new_coins_amount = coins_result[0] + coinsgained
    cursor.execute('UPDATE player_data SET coins = ? WHERE user_id = ?', (new_coins_amount, interaction.user.id))
    connection.commit()

    await interaction.response.send_message(f"You got {rolleditem.name}! ({rolleditem.rarity}) \n With a {rolleditem.percentage} chance! \n \n {coinsgained} coins earned. \n You now have {new_coins_amount} coins!")

@bot.tree.command(name="database_check", description="Check the database for user IDs.")
async def database_check(interaction: discord.Interaction):
    if interaction.user.id == 653063549496590356:
        cursor.execute('SELECT user_id FROM player_data')
        rows = cursor.fetchall()

        if rows:
            user_ids = ', \n'.join([str(row[0]) for row in rows])
            await interaction.response.send_message(f"User IDs: {user_ids}", ephemeral=True)
            logging.debug(f"{interaction.user} (id:{interaction.user.id}) sent a 'database_check' (successful)")
    else:
        await interaction.response.send_message(f"Sorry, {interaction.user.mention} you don't have perms for this :(", ephemeral=True)
        logging.debug(f"{interaction.user} (id:{interaction.user.id}) attempted to do 'database_check' (failed)")

@bot.tree.command(name="id_check", description="Check the username of an id")
@app_commands.describe(user_id="The id to check")
async def id_check(interaction: discord.Interaction, user_id: str):
    if interaction.user.id == 653063549496590356:
        try:
            user = await bot.fetch_user(int(user_id))  # Fetch the user using the ID
            await interaction.response.send_message(f"User ID: {user_id}\nUsername: {user.name}", ephemeral=True)
            logging.debug(f"{interaction.user} (id:{interaction.user.id}) sent an 'id_check' (successful)")
        except discord.NotFound:
            await interaction.response.send_message(f"User ID {user_id} not found.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Invalid user ID format. Please enter a valid number.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Sorry, {interaction.user.mention} you don't have perms for this :(", ephemeral=True)
        logging.debug(f"{interaction.user} (id:{interaction.user.id}) attempted to do 'id_check' (failed)")


bot.run(bot_token)