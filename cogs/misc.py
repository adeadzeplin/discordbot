import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
import  sounddevice as sd
from insult import insult
import insultdatabase
import os
from dotenv import load_dotenv

load_dotenv()
botit = os.getenv('BOT_ID')




class Misc(commands.Cog):
    def __init__(self,client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Misc Loaded')

    @commands.command(name='invite',help=': generates link to invite bot')
    async def invitebot(self, ctx):
        response = discord.utils.oauth_url(botit, permissions=None, guild=None, redirect_uri=None)
        await ctx.send(response)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('!i'):
            pass
        elif '<@!725508807077396581>' in message.content:
            await message.channel.send('```\n<:cardbackgrn:747592966704463965>\n```')
            await asyncio.sleep(3)
            await message.channel.purge(limit=2)


def setup(client):
    client.add_cog(Misc(client))