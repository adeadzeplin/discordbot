import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
# import  sounddevice as sd
from insult import insult
import insultdatabase
import random
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
    def returnlist(self,list,lerst):
        output = ''
        for l in list:
            if l in lerst:
                output += l + ' '
        return output
    def checklist(self,list,lerst):
        for l in list:
            if l in lerst:
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        booey = ['booey','hoo','hooh','dub','baba','bababooey','bobby','benis','boofer','coochie','cunt','cease','why','ok','bruh','dude','pussy','later','when','uh',
                 'ew','gross','dood','<:NUT:671476999558135868>']
        if message.author != self.client.user:
            if message.content.startswith('!'):
                pass
            elif '<@!725508807077396581>' in message.content:
                await message.channel.send('```\n<:cardbackgrn:747592966704463965>\n```')
                await asyncio.sleep(3)
                await message.channel.purge(limit=2)
            elif self.checklist(booey,message.content):
                # await asyncio.sleep(random.randint(1,10))
                # await message.channel.send(self.returnlist(message.content.split(' '),booey))
                print(message.content)


def setup(client):
    client.add_cog(Misc(client))