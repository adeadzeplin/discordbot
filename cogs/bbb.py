import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
# import  sounddevice as sd
from insult import insult
import insultdatabase
from discord.ext import tasks, commands

BOTID = 725508807077396581



class Bbb(commands.Cog):
    def __init__(self,client):
        self.client = client

    @tasks.loop(seconds=5)
    async def check_queue(self):
        # print('bbb queue check')
        try:
            data = self.client.pipes['s2d']['bbb'].get(0)
        except:
            data = None

        try:
            if data is None:
                data = self.client.pipes['t2d']['bbb'].get(0)
        except:
            data = None
        # if isinstance(msg, str):
        #     if msg == 'bbb':

        if data != None:
            # print(data['filename'])
            await self.bbb(None, deleteflag=False, Called_from_Queue=True, FileName=data['filename'], No_random_delay=True)



        # if self.client.que

    @commands.Cog.listener()
    async def on_ready(self):
        await self.check_queue.start()
        print(f'BBB Loaded')
    def load_soundfiles(self):
        import os
        soundpaths = []
        for filename in os.listdir('./sounds'):
            if filename.endswith('.wav') or filename.endswith('.mp3'):
                soundpaths.append('./sounds/'+filename)
        return soundpaths


    @commands.command(name='BBB',aliases = ['bbb','b','B'] )
    async def bbb(self, ctx, *, number_of_bs=1, deleteflag=True, Called_from_Queue=False,FileName=None, No_random_delay=False):
        if deleteflag:
            await ctx.channel.purge(limit=1)
        if ctx == None:
            server = self.client.get_guild(437778883744628736)
        else:
            server = ctx.message.guild
        voicechannels = []
        for chan in server.channels:
            if isinstance(chan,discord.VoiceChannel):
                if len(chan.members)>0:
                    voicechannels.append(chan)
        if len(voicechannels) == 0:
            return
        # if number_of_bs >= 6:
        #     await ctx.send(f'{ctx.message.author} tried to be cancerous by trying to have the bot say {number_of_bs}')
        #     number_of_bs = 5

        for i in range(number_of_bs):
            # await asyncio.sleep(np.random.randint(60*10))
            randindex = np.random.randint(len(voicechannels))
            randchannel = voicechannels[randindex]

            # skipjoinflag = False
            # for dude in randchannel.members:
            #     if dude.id == BOTID:
            #         skipjoinflag = True
            # await asyncio.sleep(np.random.randint(3)) # np.random.randint(60*2)
            # if skipjoinflag == False:
            vc = await randchannel.connect(timeout=60.0,reconnect=True)
            if not No_random_delay:
                await asyncio.sleep(np.random.randint(1,8))

            snds = self.load_soundfiles()
            # for times in range(0,np.random.randint(1,3)):
            # print(len(vids))
            # print(Called_from_Queue)
            if Called_from_Queue == True and FileName != None :
                # print(snds)
                FileName = f'./sounds/{FileName}.wav'
                if FileName in snds:
                    randsnd = snds.index(FileName)
                else:
                    randsnd = np.random.randint(len(snds))
            else:
                randsnd = np.random.randint(len(snds))


            for dude in vc.channel.members: # Play function call happens in a loop checking if the bot is still conectted to voice. Because the bot can be disconnected before playing and will break everything
                if dude.id == BOTID:
                    vc.play(discord.FFmpegPCMAudio(snds[randsnd]))#,executable='C:/ffmpeg/bin/ffmpeg',options=['-guess_layout_max 0','-i']
                    break

            if ctx != None:
                print(f"bbbbing in {ctx.message.guild} sound file {snds[randsnd]}")
            else:
                print(f"bbbbing sound file: '{snds[randsnd].replace('./sounds/','').replace('.wav','')}'")
            while vc.is_playing():
                await asyncio.sleep(.2)
            await asyncio.sleep(.2)

            disconflag = False

            for dude in vc.channel.members:
                if dude.id == BOTID:
                    disconflag = True
            if disconflag == True:
                await vc.disconnect(force=True)
            await asyncio.sleep(2)


            print(f"{i+1} of {number_of_bs}")



        # for i,cli in enumerate(self.client.voice_clients):
        #     await self.client.voice_clients[i].disconnect()
        if ctx != None:
            print(f"{ctx.message.author} called the b command in {ctx.message.guild} and it ran {number_of_bs} times")
def setup(client):
    client.add_cog(Bbb(client))