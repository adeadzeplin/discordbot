import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
import  sounddevice as sd
from insult import insult
import insultdatabase
from discord.ext import tasks, commands



class Bbb(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'BBB Loaded')
    def load_soundfiles(self):
        import os
        soundpaths = []
        for filename in os.listdir('./sounds'):
            if filename.endswith('.wav') or filename.endswith('.mp3'):
                soundpaths.append('./sounds/'+filename)
        return soundpaths

    @tasks.loop(seconds=8.0)
    async def do_bbb(self,ctx):
        print("BBB LOOP ACTIVE")
        await self.bbb(ctx, deleteflag=False)

    @commands.command(aliases = ['sb'] )
    async def startb(self, ctx, *, number_of_b=1):
        try:
            self.do_bbb.start(ctx)
            await ctx.send(f"Comensing Operation nonsense")
        except:
            await ctx.send(f"Operation nonsense is aleady in effect")



    @commands.command(aliases=['bs'])
    async def stopb(self, ctx, *, number_of_b=1):
        try:
            self.do_bbb.stop()
            await ctx.send(f"Stoping Operation nonsense")
            print("stopping the looping")
        except:
            pass


    @commands.command(name='BBB',aliases = ['bbb','b','B'] )
    async def bbb(self, ctx, *, number_of_bs=1, deleteflag = True):
        if deleteflag:
            await ctx.channel.purge(limit=1)
        server = ctx.message.guild
        voicechannels = []
        for chan in server.channels:
            if isinstance(chan,discord.VoiceChannel):
                voicechannels.append(chan)

        # if number_of_bs >= 6:
        #     await ctx.send(f'{ctx.message.author} tried to be cancerous by trying to have the bot say {number_of_bs}')
        #     number_of_bs = 5

        for i in range(number_of_bs):
            # await asyncio.sleep(np.random.randint(60*10))
            randindex = np.random.randint(len(voicechannels))

            randchannel = voicechannels[randindex]
            await asyncio.sleep(np.random.randint(3)) # np.random.randint(60*2)
            try:
                vc = await randchannel.connect(timeout=60.0,reconnect=True)
                await asyncio.sleep(np.random.randint(1,8))
            except:
                pass
            vids = self.load_soundfiles()
            print(len(vids))
            randvid = np.random.randint(len(vids))
            vc.play(discord.FFmpegPCMAudio(vids[randvid],executable='C:/ffmpeg/bin/ffmpeg'))
            while vc.is_playing():
                await asyncio.sleep(.1)
            await asyncio.sleep(.5)
            try:
                await vc.disconnect(force=True)
            except:
                pass
            print(f"bbbbing in {ctx.message.guild} sound file {vids[randvid]}")
            print(f"{i+1} of {number_of_bs}")



        # for i,cli in enumerate(self.client.voice_clients):
        #     await self.client.voice_clients[i].disconnect()
        print(f"{ctx.message.author} called the b command in {ctx.message.guild} and it ran {number_of_bs} times")
def setup(client):
    client.add_cog(Bbb(client))