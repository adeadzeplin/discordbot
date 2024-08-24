import random
import discord
from discord.ext import commands
import asyncio
import pickle
from discord import app_commands
from typing import List
import os
from discord.errors import ClientException, ConnectionClosed
import logging

AUDIO_DELAY_FILE = "audio_delay.txt"

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
        self.reset_state_task = self.bot.loop.create_task(self.periodic_state_check())
        self.api_call_delay = 1
        self.audio_delay = self.load_delay(AUDIO_DELAY_FILE, default=1)

    def load_delay(self, file_path, default):
        try:
            with open(file_path, "r") as file:
                return float(file.read().strip())
        except FileNotFoundError:
            self.save_delay(file_path, default)
            return default

    def save_delay(self, file_path, delay):
        with open(file_path, "w") as file:
            file.write(str(delay))

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
        
        try:
            await asyncio.sleep(self.api_call_delay)
            await self.bot.change_presence(activity=activity)
            
            for guild in self.bot.guilds:
                new_nickname = f"E-bot : {queue_size}" if queue_size > 0 else "E-bot"
                
                if guild.me.nick != new_nickname:
                    try:
                        await asyncio.sleep(self.api_call_delay)
                        await guild.me.edit(nick=new_nickname)
                    except discord.errors.Forbidden:
                        self.logger.warning(f"Unable to change nickname in guild {guild.name}. Missing permissions.")
                    except discord.errors.HTTPException as e:
                        if e.status == 429:
                            self.logger.warning(f"Rate limited while updating nickname in guild {guild.name}. Skipping.")
                        else:
                            self.logger.error(f"Error updating nickname in guild {guild.name}: {str(e)}")
        except discord.errors.HTTPException as e:
            if e.status == 429:
                self.logger.warning("Rate limited while updating presence. Skipping.")
            else:
                self.logger.error(f"Error updating presence: {str(e)}")

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
        await ctx.send(f"+{number_of_bs} {'random' if sound is None else sound}")
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
        await ctx.send(f"+1 sound:'{filename}'")
        await self.update_presence()
        if not self.is_playing:
            self.play_task = asyncio.create_task(self.play_queue(ctx))

    @commands.hybrid_command(name='pause', help='Pause the current playback')
    async def pause(self, ctx: commands.Context):
        if self.current_voice_client and self.current_voice_client.is_playing():
            self.current_voice_client.pause()
            self.is_paused = True
            await ctx.send("Playback paused.")
        elif self.is_paused:
            await ctx.send("Playback is already paused.")
        else:
            await ctx.send("Nothing is currently playing.")

    @commands.hybrid_command(name='resume', help='Resume the paused playback')
    async def resume(self, ctx: commands.Context):
        if self.current_voice_client and self.is_paused:
            self.current_voice_client.resume()
            self.is_paused = False
            await ctx.send("Playback resumed.")
        elif not self.is_paused and self.current_voice_client and self.current_voice_client.is_playing():
            await ctx.send("Playback is already running.")
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
                        try:
                            await self.current_voice_client.move_to(voice_channel)
                        except ClientException as e:
                            if str(e) == "Already connected to a voice channel.":
                                await self.current_voice_client.disconnect()
                                self.current_voice_client = await voice_channel.connect()
                            else:
                                raise
                    await asyncio.sleep(self.audio_delay)
                    await self._bbb_logic(sound)
                    while self.current_voice_client and self.current_voice_client.is_playing():
                        await asyncio.sleep(0.1)
                except ClientException as e:
                    if str(e) == "Already playing audio.":
                        self.logger.warning("Already playing audio. Stopping current playback.")
                        self.current_voice_client.stop()
                        await asyncio.sleep(0.1)
                        continue
                    else:
                        self.logger.error(f"ClientException in play_queue: {str(e)}")
                except ConnectionClosed:
                    self.logger.error("Connection closed. Attempting to reconnect...")
                    await self.reconnect(voice_channel)
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error in play_queue: {str(e)}")
                    break
                
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
        except ClientException as e:
            if str(e) == "Already playing audio.":
                self.logger.warning("Already playing audio. Stopping current playback.")
                self.current_voice_client.stop()
                await asyncio.sleep(0.1)
                self.current_voice_client.play(discord.FFmpegPCMAudio(sound_path))
            else:
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

    async def periodic_state_check(self):
        while not self.bot.is_closed():
            await self.check_and_reset_state()
            await asyncio.sleep(5)

    async def check_and_reset_state(self):
        if self.is_playing and not self.current_voice_client:
            self.logger.warning("Detected inconsistent state. Resetting...")
            self.is_playing = False
            self.is_paused = False
            self.current_sound = None
            await self.update_presence()
            
            if self.queue:
                _, _, voice_channel = self.queue[-1]
                try:
                    self.current_voice_client = await voice_channel.connect()
                    self.logger.info("Rejoined the voice channel.")
                except ClientException as e:
                    if str(e) == "Not connected to voice.":
                        self.logger.warning("Not connected to voice. Skipping rejoin.")
                    else:
                        self.logger.error(f"Failed to rejoin the voice channel: {str(e)}")

    def cog_unload(self):
        self.reset_state_task.cancel()

    @commands.hybrid_command(name='setapidelay', help='Set the delay between API calls')
    async def set_api_delay(self, ctx: commands.Context, delay: float):
        self.api_call_delay = delay
        await ctx.send(f"API call delay set to {delay} seconds.")

    @commands.hybrid_command(name='setaudiodelay', help='Set the delay between audio files being played')
    async def set_audio_delay(self, ctx: commands.Context, delay: float):
        if delay < 1:
            await ctx.send("Minimum audio delay is 1 second.")
            return
        if delay > 600:
            await ctx.send("Maximum audio delay is 10 minutes.")
            return
        self.audio_delay = delay
        self.save_delay(AUDIO_DELAY_FILE, delay)
        await ctx.send(f"Audio delay set to {delay} seconds.")

async def setup(bot):
    await bot.add_cog(Bbb(bot))
    await bot.tree.sync()