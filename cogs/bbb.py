import random
import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
from discord.ext import tasks
import pickle
from discord import app_commands
from typing import List
import os
from discord.errors import ClientException
from discord.errors import ConnectionClosed
import logging

# TODO: Consider moving this to a configuration file
BOTID = 725508807077396581

class Bbb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_map_template = {"total_plays": 0, "longest_chain": 0}
        self.sound_data = {}
        self.prev = ""
        self.consect_count = 1
        self.sound_history = []
        self.snds = self.load_soundfiles()
        self.queue = asyncio.Queue()
        self.is_playing = False
        self.is_paused = False
        self.current_voice_client = None
        self.logger = logging.getLogger('discord_bot')
        self.play_task = None
        self.current_sound = None
        self.bot.loop.create_task(self.initialize_presence())

    async def initialize_presence(self):
        await self.bot.wait_until_ready()
        await self.update_presence()

    def load_soundfiles(self):
        return [f'./sounds/{filename}' for filename in os.listdir('./sounds') if filename.endswith(('.wav', '.mp3'))]

    async def sound_name_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        sound_names = [s.split('/')[-1].split('.')[0] for s in self.snds]
        return [app_commands.Choice(name=sound, value=sound) for sound in sound_names if current.lower() in sound.lower()][:25]

    async def update_presence(self):
        queue_size = self.queue.qsize()
        activity = discord.Activity(type=discord.ActivityType.playing, name=f"{self.current_sound or 'Nothing'}")
        for guild in self.bot.guilds:
            try:
                if queue_size > 0:
                    new_nickname = f"E-bot : {queue_size}"
                else:
                    new_nickname = "E-bot"
                await guild.me.edit(nick=new_nickname)
            except discord.errors.Forbidden:
                self.logger.warning(f"Unable to change nickname in guild {guild.name}. Missing permissions.")
        await self.bot.change_presence(activity=activity)

    @commands.hybrid_command(name='bbb', aliases=['b', 'B'], help='Add random sounds to the queue')
    @app_commands.describe(number_of_bs="Number of random sounds to add", sound="The sound to play (optional)")
    @app_commands.autocomplete(sound=sound_name_autocomplete)
    async def bbb(self, ctx: commands.Context, number_of_bs: int = 1, sound: str = None):
        voice_state = ctx.author.voice
        if voice_state is None:
            await ctx.send("You need to be in a voice channel to use this command.")
            return
        voice_channel = voice_state.channel
        for _ in range(number_of_bs):
            await self.queue.put(('random', sound, voice_channel))
        await ctx.send(f"Added {number_of_bs} {'random' if sound is None else sound} sound(s) to the queue.")
        await self.update_presence()
        if not self.is_playing:
            self.play_task = asyncio.create_task(self.play_queue(ctx))

    @commands.hybrid_command(name='bfile', aliases=['bf', 'Bf'], help="Add a specific sound file to the front of the queue")
    @app_commands.describe(filename="The name of the sound file to play")
    @app_commands.autocomplete(filename=sound_name_autocomplete)
    async def bbb_file(self, ctx: commands.Context, *, filename: str = "1bit"):
        voice_state = ctx.author.voice
        if voice_state is None:
            await ctx.send("You need to be in a voice channel to use this command.")
            return
        voice_channel = voice_state.channel
        await self.queue.put(('file', filename, voice_channel))
        await ctx.send(f"Added '{filename}' to the queue.")
        await self.update_presence()
        if not self.is_playing:
            self.play_task = asyncio.create_task(self.play_queue(ctx))

    @commands.hybrid_command(name='pause', help='Pause the current playback')
    async def pause(self, ctx: commands.Context):
        if self.current_voice_client and self.current_voice_client.is_playing():
            self.current_voice_client.pause()
            self.is_paused = True
            await ctx.send("Playback paused.")
        else:
            await ctx.send("Nothing is currently playing.")

    @commands.hybrid_command(name='resume', help='Resume the paused playback')
    async def resume(self, ctx: commands.Context):
        if self.current_voice_client and self.is_paused:
            self.current_voice_client.resume()
            self.is_paused = False
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("Nothing is paused.")

    async def play_queue(self, ctx):
        self.is_playing = True
        try:
            while not self.queue.empty():
                if self.is_paused:
                    await asyncio.sleep(1)
                    continue

                play_type, sound, voice_channel = await self.queue.get()
                await self.update_presence()
                try:
                    if not self.current_voice_client or not self.current_voice_client.is_connected():
                        self.current_voice_client = await voice_channel.connect()
                    elif self.current_voice_client.channel != voice_channel:
                        await self.current_voice_client.move_to(voice_channel)
                    
                    await self._bbb_logic(sound)
                    while self.current_voice_client and self.current_voice_client.is_playing():
                        await asyncio.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"Error playing sound: {str(e)}")
                    if isinstance(e, discord.ClientException) and str(e) == "Already playing audio.":
                        self.current_voice_client.stop()
                        await asyncio.sleep(0.1)
                        continue
                    elif isinstance(e, discord.errors.ConnectionClosed):
                        self.logger.error("Connection closed. Attempting to reconnect...")
                        await self.reconnect(voice_channel)
                        continue
                
                await asyncio.sleep(1)
        finally:
            self.is_playing = False
            self.current_sound = None
            if self.current_voice_client and self.current_voice_client.is_connected():
                await self.current_voice_client.disconnect()
            self.current_voice_client = None
            await self.update_presence()

    async def reconnect(self, voice_channel):
        try:
            if self.current_voice_client:
                await self.current_voice_client.disconnect(force=True)
            self.current_voice_client = await voice_channel.connect()
        except Exception as e:
            self.logger.error(f"Failed to reconnect: {str(e)}")

    async def _bbb_logic(self, sound: str = None):
        if sound is not None:
            sound_path = f'./sounds/{sound}.wav'
            if sound_path in self.snds:
                randsnd = self.snds.index(sound_path)
            else:
                randsnd = random.randint(0, len(self.snds) - 1)
        else:
            randsnd = random.randint(0, len(self.snds) - 1)
        
        if self.current_voice_client.is_playing():
            self.current_voice_client.stop()
        
        sound_path = self.snds[randsnd]
        self.current_sound = sound_path.split("/")[-1].split(".")[0]
        await self.update_presence()
        
        try:
            self.current_voice_client.play(discord.FFmpegPCMAudio(sound_path))
        except Exception as e:
            self.logger.error(f"Error playing sound file: {str(e)}")
            raise
        
        if sound_path not in self.sound_data:
            self.sound_data[sound_path] = self.data_map_template.copy()
        
        self.sound_data[sound_path]["total_plays"] += 1
        
        if sound_path == self.prev:
            self.consect_count += 1
            if self.consect_count > self.sound_data[sound_path]["longest_chain"]:
                self.sound_data[sound_path]["longest_chain"] = self.consect_count
        else:
            self.consect_count = 1
        
        self.prev = sound_path
        
        self.sound_history.append(self.current_sound)
        
        self.update_bbb_log()
        
        self.logger.info(f"Played sound file {self.current_sound}")

    def update_bbb_log(self):
        with open("sound_leaderboard.pickle", "wb") as f:
            pickle.dump(self.sound_data, f)

    def load_bbb_log(self):
        try:
            with open("sound_leaderboard.pickle", "rb") as f:
                self.sound_data = pickle.load(f)
        except:
            self.sound_data = {}

    def get_top_songs_played(self):
        return sorted([(k.split("/")[-1].split(".")[0], v["total_plays"]) for k, v in self.sound_data.items()], key=lambda x: x[1], reverse=True)

    def get_top_songs_chained(self):
        return sorted([(k.split("/")[-1].split(".")[0], v["longest_chain"]) for k, v in self.sound_data.items()], key=lambda x: x[1], reverse=True)

async def setup(bot):
    await bot.add_cog(Bbb(bot))
    await bot.tree.sync()