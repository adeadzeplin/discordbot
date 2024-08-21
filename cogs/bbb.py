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
import pickle

# TODO: Consider moving this to a configuration file
BOTID = 725508807077396581

class Bbb(commands.Cog):
    def __init__(self,client):
        self.client = client

        # Template for storing sound data
        self.data_map_template = {
            "total_plays": 0,
            "longest_chain": 0
        }
        self.sound_data = {}
        self.prev = ""
        self.consect_count = 1

        self.sound_history = []

    @tasks.loop(seconds=1)
    async def check_queue(self):
        # REVIEW: Consider implementing proper error handling here
        try:
            data = self.client.pipes['s2d']['bbb'].get(0)
        except:
            data = None

        try:
            if data is None:
                data = self.client.pipes['t2d']['bbb'].get(0)
        except:
            data = None

        if data != None:
            # TODO: Consider adding logging here
            await self.bbb(None, deleteflag=False, Called_from_Queue=True, FileName=data['filename'], No_random_delay=True)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.check_queue.start()
        self.load_bbb_log()
        print(f'BBB Loaded')

    def load_pfps(self):
        import os
        pfp_paths = []
        for filename in os.listdir('./pfps'):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                pfp_paths.append('./pfps/' + filename)
        return pfp_paths

    def update_bbb_log(self):
        pathname = f"sound_leaderboard.pickle"
        with open(pathname, "wb") as f:
            pickle.dump(self.sound_data, f)

    def load_bbb_log(self):
        try:
            with open("sound_leaderboard.pickle", "rb") as f:
                self.sound_data = pickle.load(f)
        except:
            self.sound_data = {}
    def plays_sort(self,data):
        return data["total_plays"]
    def chain_sort(self,data):
        return data["longest_chain"]

    def get_top_songs_played(self):
        self.temp = list(self.sound_data.keys())
        sorted(self.temp, key=self.plays_sort)
        out = []
        for t in self.temp:
            out.append((t,self.sound_data[t]["total_plays"]))
        return out
    def get_top_songs_chained(self):
        self.temp = list(self.sound_data.keys())
        sorted(self.temp, key=self.plays_sort)
        out = []
        for t in self.temp:
            out.append((t,self.sound_data[t]["longest_chain"]))
        return out

    def load_soundfiles(self):
        import os
        soundpaths = []
        for filename in os.listdir('./sounds'):
            if filename.endswith('.wav') or filename.endswith('.mp3'):
                soundpaths.append('./sounds/'+filename)
        return soundpaths

    @commands.command(name='BHistory', aliases=['bh', 'Bh'], help='Display the last played sound names', brief="Show sound history")
    async def bbb_history(self, ctx, *, num=5):
        """
        Display the last played sound names.
        
        Usage: !BHistory [number]
        Example: !BHistory 10
        
        [number] - Optional: Number of sound names to display (default: 5)
        """
        # TODO: Consider adding error handling for invalid 'num' values
        await ctx.channel.purge(limit=1)

        history_string = 'Displaying the last ' + str(num) + " sound names played:\n"
        for it, s in enumerate(reversed(self.sound_history)):
            history_string+= s + '\n'
            if it >= num:
                break
        await ctx.channel.send(history_string)

    @commands.command(name='bchain', aliases=['bc', 'Bc'], help="Display information about chained sounds", brief="Show chained sounds")
    async def bbb_Chain(self, ctx, *, num=5):
        """
        Display information about chained sounds.
        
        Usage: !bchain [number]
        Example: !bchain 10
        
        [number] - Optional: Number of chained sounds to display (default: 5)
        """
        pass
        #save point
        #adding a command to display the most plays sounds.
        #add another command for chained sounds.

    @commands.command(name='Bfile', aliases=['bf', 'Bf'], help="Play a specific sound file", brief="Play sound file")
    async def bbb_file(self, ctx, *, filename="1bit"):
        """
        Play a specific sound file.
        
        Usage: !Bfile <filename>
        Example: !Bfile mysound
        
        <filename> - The name of the sound file to play (default: 1bit)
        """
        await self.bbb(ctx, deleteflag=False, Called_from_Queue=True, FileName=filename, No_random_delay=True)

    @commands.command(name='BBB', aliases=['bbb', 'b', 'B'], help='Play a set of n random sounds')
    async def bbb(self, ctx, *, number_of_bs=1, deleteflag=True, Called_from_Queue=False,FileName=None, No_random_delay=False):
        # REVIEW: This method is quite long and complex. Consider breaking it down into smaller functions
        if deleteflag:
            await ctx.channel.purge(limit=1)
        if ctx == None:
            server = self.client.get_guild(877713599894798367)#911398925804646421
        else:
            server = ctx.message.guild

        connected = False
        disconnect_rate = 0
        snds = self.load_soundfiles()
        vc = None
        for i in range(number_of_bs):
            if vc is not None:
                connected = vc.is_connected()
            print("we are connected:", connected)
            if connected == False:

                voicechannels = [].copy()
                for chan in server.channels:
                    if isinstance(chan, discord.VoiceChannel):
                        if len(chan.members) > 0:
                            voicechannels.append(chan)
                if len(voicechannels) == 0:
                    return
                
                randindex = np.random.randint(len(voicechannels))
                randchannel = voicechannels[randindex]

                if vc is not None:
                    await vc.disconnect(force=True)
                vc = await randchannel.connect(timeout=20.0,reconnect=True)
                connected = vc.is_connected()
                print("we arent conneced... Now we are:",connected)
            
            if Called_from_Queue == True and FileName != None :
                FileName = f'./sounds/{FileName}.wav'
                if FileName in snds:
                    randsnd = snds.index(FileName)
                else:
                    randsnd = np.random.randint(len(snds))
            else:
                randsnd = np.random.randint(len(snds))
            #
            #
            #
            #
            #
            #
            for dude in vc.channel.members: # Play function call happens in a loop checking if the bot is still conectted to voice. Because the bot can be disconnected before playing and will break everything
                if dude.id == BOTID:
                    vc.play(discord.FFmpegPCMAudio(snds[randsnd]))#,executable='C:/ffmpeg/bin/ffmpeg',options=['-guess_layout_max 0','-i']
                    break
            
            if snds[randsnd] not in self.sound_data:
                self.sound_data[snds[randsnd]] = self.data_map_template.copy()
            
            self.sound_data[snds[randsnd]]["total_plays"] += 1
            
            if snds[randsnd] == self.prev:
                self.consect_count += 1
                if self.consect_count > self.sound_data[snds[randsnd]]["longest_chain"]:
                    self.sound_data[snds[randsnd]]["longest_chain"] = self.consect_count
                    
                    for dude in vc.channel.members:
                        if dude.id == BOTID:
                            vc.play(discord.FFmpegPCMAudio(snds[   snds.index("wombocomboa")    ]))
                            break
            else:
                self.consect_count = 1
            
            self.prev = snds[randsnd]

            if ctx != None:
                print(f"bbbbing in {ctx.message.guild} sound file {snds[randsnd]}")
            else:
                print(f"bbbbing sound file: '{snds[randsnd].replace('./sounds/','').replace('.wav','')}'")

            if not No_random_delay:
                await asyncio.sleep(np.random.randint(5, 20 ))

            while vc.is_playing():
                print(f"still playing")
                await asyncio.sleep(.2)
            await asyncio.sleep(2)
            
            sound_name = snds[randsnd]
            sound_name = sound_name.split(".")[1]
            sound_name = sound_name.split("/")
            sound_name = sound_name[len(sound_name) - 1]
            self.sound_history.append(sound_name)

            print(f"{i+1} of {number_of_bs}")
            if i%10==0:
                self.update_bbb_log()
            
        if connected == True:
            for dude in vc.channel.members:
                if dude.id == BOTID:
                    disconflag = True
            if disconflag == True:
                await vc.disconnect(force=True)
            await dude.edit(nick=None)
        self.update_bbb_log()
        if ctx != None:
            print(f"{ctx.message.author} called the b command in {ctx.message.guild} and it ran {number_of_bs} times")

async def setup(client):
    await client.add_cog(Bbb(client))

# OVERALL NOTES:
# TODO: Implement comprehensive error handling throughout the script
# TODO: Consider adding logging for better debugging and monitoring
# REVIEW: The 'bbb' method is quite long and complex. Consider breaking it down into smaller, more manageable functions
# TODO: Consider moving configuration values (like file paths and bot ID) to a separate config file
# REVIEW: Evaluate the necessity of each imported module