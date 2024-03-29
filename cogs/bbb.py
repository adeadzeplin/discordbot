import random

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

    @tasks.loop(seconds=1)
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

    def load_pfps(self):
        import os
        pfp_paths = []
        for filename in os.listdir('./pfps'):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                pfp_paths.append('./pfps/' + filename)
        return pfp_paths

    def load_soundfiles(self):
        import os
        soundpaths = []
        for filename in os.listdir('./sounds'):
            if filename.endswith('.wav') or filename.endswith('.mp3'):
                soundpaths.append('./sounds/'+filename)
        return soundpaths

    @commands.command(name='Bfile', aliases=['bf', 'Bf'])
    async def bbb_file(self, ctx, *, filename="1bit"):
        await self.bbb(ctx, deleteflag=False, Called_from_Queue=True, FileName=filename, No_random_delay=True)


    @commands.command(name='BBB',aliases = ['bbb','b','B'] )
    async def bbb(self, ctx, *, number_of_bs=1, deleteflag=True, Called_from_Queue=False,FileName=None, No_random_delay=False):
        if deleteflag:
            await ctx.channel.purge(limit=1)
        if ctx == None:
            server = self.client.get_guild(877713599894798367)#911398925804646421
        else:
            server = ctx.message.guild

        # if number_of_bs >= 6:
        #     await ctx.send(f'{ctx.message.author} tried to be cancerous by trying to have the bot say {number_of_bs}')
        #     number_of_bs = 5
        connected = False
        disconnect_rate = 0
        snds = self.load_soundfiles()

        for i in range(number_of_bs):
            if connected == False:
                voicechannels = [].copy()
                for chan in server.channels:
                    if isinstance(chan, discord.VoiceChannel):
                        if len(chan.members) > 0:
                            voicechannels.append(chan)
                if len(voicechannels) == 0:
                    return

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
                connected = True




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




            if not No_random_delay:
                await asyncio.sleep(np.random.randint(2, 10 + disconnect_rate))


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
            await asyncio.sleep(2)

            sound_name = snds[randsnd]
            sound_name = sound_name.split(".")[1]
            sound_name = sound_name.split("/")
            sound_name = sound_name[len(sound_name) - 1]
            # print(sound_name)
            for dude in vc.channel.members:
                if dude.id == BOTID:
                    break
            #await dude.edit(nick=sound_name)


            disconflag = False
            if connected == True:
                rand_diconnect_rate_max = 10
                rand_disconnect = random.randint(0,rand_diconnect_rate_max)



                if rand_disconnect <= disconnect_rate:
                    for dude in vc.channel.members:
                        if dude.id == BOTID:
                            disconflag = True
                            break
                    if disconflag == True:
                        # print("Disconnecting ", rand_disconnect)
                        await vc.disconnect(force=True)
                        connected = False
                        #  randomly change the rate of randomly disconnecting
                        if 0 == random.randint(0,1):
                            disconnect_rate = random.randint(0, rand_diconnect_rate_max)

                    await asyncio.sleep(5)


            print(f"{i+1} of {number_of_bs}")

        if connected == True:
            for dude in vc.channel.members:
                if dude.id == BOTID:
                    disconflag = True
            if disconflag == True:
                await vc.disconnect(force=True)
            await dude.edit(nick=None)

        # for i,cli in enumerate(self.client.voice_clients):
        #     await self.client.voice_clients[i].disconnect()
        if ctx != None:
            print(f"{ctx.message.author} called the b command in {ctx.message.guild} and it ran {number_of_bs} times")
def setup(client):
    client.add_cog(Bbb(client))