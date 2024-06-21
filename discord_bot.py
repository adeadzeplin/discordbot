# RUN THIS FILE TO START THE BOT

import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)



# @client.command()
# async def load(ctx,extension):
#     client.load_extension(f"cogs.{extension}")
#     await ctx.send(f"Loaded cog: {extension}")
# @client.command()
# async def unload(ctx,extension):
#     client.unload_extension(f"cogs.{extension}")
#     await ctx.send(f"Unoaded cog: {extension}")
#
# @client.command()
# async def reload(ctx,extension):
#     client.unload_extension(f"cogs.{extension}")
#     client.load_extension(f"cogs.{extension}")
#     await ctx.send(f"Reloaded cog: {extension}")
#
# @client.command()
# async def clear(ctx):
#     print(f'Bot removed everything in the channel: {ctx.channel.name}')
#     await ctx.channel.purge()

def init_discord_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            asyncio.run(client.load_extension(f'cogs.{filename[:-3]}'))

@client.event
async def on_ready():
    print(f'Bot logged in as : {client.user.name}')
    # print(client.user.id)
    print('------')

def run_discordbot(p):
    init_discord_cogs()
    client.pipes = p
    client.run(TOKEN,log_handler=None)


if __name__ == "__main__":
    run_discordbot("where am i?")

