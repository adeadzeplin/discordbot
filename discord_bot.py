# RUN THIS FILE TO START THE BOT

import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Disable logging
import logging
logging.getLogger('discord').setLevel(logging.ERROR)
logging.getLogger('discord.http').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

async def init_discord_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
                print(f'{filename[:-3]} Loaded')
            except Exception as e:
                print(f'Failed to load {filename[:-3]}: {str(e)}')

@client.event
async def on_ready():
    print(f'Bot logged in as : {client.user.name}')
    print('------')
    await init_discord_cogs()

def run_discordbot(p=None):
    if p:
        client.pipes = p
    client.run(TOKEN, log_handler=None)

if __name__ == "__main__":
    run_discordbot()