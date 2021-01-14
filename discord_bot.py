# RUN THIS FILE TO START THE BOT

import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
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


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.event
async def on_ready():
    print(f'Bot logged in as : {client.user.name}')
    # print(client.user.id)
    print('------')

def run_discordbot(q):
    client.que = q
    client.run(TOKEN)


if __name__ == "__main__":
    run_discordbot("where am i?")
