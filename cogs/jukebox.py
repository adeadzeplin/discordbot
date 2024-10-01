import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from collections import deque
import re
import logging

class Jukebox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sound_dir = 'sounds'  # Directory for sound files
        self.is_playing = False
        self.api_delay = 1  # Delay in seconds before each API call
        self.bot.loop.create_task(self.initialize_queue())

    async def initialize_queue(self):
        await self.bot.wait_until_ready()
        self.queue = await self.get_queue_from_nickname()
        logging.info(f"Initialized queue with size: {len(self.queue)}")

    async def get_queue_from_nickname(self):
        for guild in self.bot.guilds:
            bot_member = guild.me
            nickname = bot_member.nick or bot_member.name
            queue_size = self.extract_queue_size(nickname)
            logging.info(f"Read queue size {queue_size} from nickname in guild {guild.name}")
            return deque([None] * queue_size)
        logging.warning("No guilds found to read queue size from nickname")
        return deque()

    def extract_queue_size(self, nickname):
        match = re.search(r'\[(\d+)\]', nickname)
        size = int(match.group(1)) if match else 0
        logging.info(f"Extracted queue size {size} from nickname: {nickname}")
        return size

    async def update_queue_size(self, size):
        updated = False
        for guild in self.bot.guilds:
            try:
                old_nickname = guild.me.nick or guild.me.name
                new_nickname = f"eBot [{size}]"
                if old_nickname != new_nickname:
                    await self.api_call(guild.me.edit(nick=new_nickname))
                    logging.info(f"Updated queue size to {size} in guild {guild.name}")
                    updated = True
                else:
                    logging.info(f"Nickname already up to date in guild {guild.name}")
            except discord.Forbidden:
                logging.error(f"Bot doesn't have permission to change its nickname in guild {guild.name}")
            except Exception as e:
                logging.error(f"Error updating nickname in guild {guild.name}: {str(e)}")
        
        if not updated:
            logging.warning(f"Failed to update nickname in any guild to reflect queue size {size}")

    async def api_call(self, coroutine):
        await asyncio.sleep(self.api_delay)
        return await coroutine

    async def get_sound_files(self):
        return [f for f in os.listdir(self.sound_dir) if f.endswith('.wav')]

    async def sound_file_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        sound_files = await self.get_sound_files()
        matching_files = [f for f in sound_files if current.lower() in f.lower()]
        selected_files = random.sample(matching_files, min(25, len(matching_files)))
        selected_files.sort()
        return [app_commands.Choice(name=f, value=f) for f in selected_files]

    @commands.command(aliases=['j'])
    async def join(self, ctx):
        """Join the user's voice channel"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await self.api_call(channel.connect())
        else:
            await self._send_error(ctx, "You need to be in a voice channel to use this command.")

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        """Leave the voice channel"""
        if ctx.voice_client:
            await self.update_queue_size(0)
            self.is_playing = False
            await self.api_call(ctx.voice_client.disconnect())
            logging.info("Bot disconnected from voice channel")
        else:
            await self._send_error(ctx, "I'm not in a voice channel.")

    @commands.command(aliases=['p'])
    async def play(self, ctx, sound_file: str = None, count: int = 1):
        """Add sound file(s) to the queue"""
        await self._add_to_queue(ctx, sound_file, count, priority=False)

    @app_commands.command(name="play", description="Add sound file(s) to the queue")
    @app_commands.autocomplete(sound_file=sound_file_autocomplete)
    async def play_slash(self, interaction: discord.Interaction, sound_file: str = None, count: int = 1):
        await self._add_to_queue(interaction, sound_file, count, priority=False)

    @commands.command(aliases=['pn'])
    async def play_next(self, ctx, sound_file: str = None):
        """Add a sound file to the front of the queue"""
        await self._add_to_queue(ctx, sound_file, 1, priority=True)

    @app_commands.command(name="play_next", description="Add a sound file to the front of the queue")
    @app_commands.autocomplete(sound_file=sound_file_autocomplete)
    async def play_next_slash(self, interaction: discord.Interaction, sound_file: str = None):
        await self._add_to_queue(interaction, sound_file, 1, priority=True)

    async def _add_to_queue(self, ctx_or_interaction, sound_file: str = None, count: int = 1, priority: bool = False):
        if isinstance(ctx_or_interaction, discord.Interaction):
            await self.api_call(ctx_or_interaction.response.defer(ephemeral=True))
            ctx = await self.bot.get_context(ctx_or_interaction)
        else:
            ctx = ctx_or_interaction

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice:
                try:
                    await self.api_call(ctx.author.voice.channel.connect())
                    logging.info(f"Connected to voice channel: {ctx.author.voice.channel}")
                except Exception as e:
                    await self._send_error(ctx, f"Failed to connect to voice channel: {str(e)}")
                    logging.error(f"Failed to connect to voice channel: {str(e)}")
                    return
            else:
                await self._send_error(ctx, "You need to be in a voice channel to use this command.")
                logging.error("User not in a voice channel when trying to add to queue")
                return

        sound_files = await self.get_sound_files()
        if not sound_files:
            await self._send_error(ctx, "No sound files found in the sounds directory.")
            logging.error("No sound files found in the sounds directory")
            return

        if sound_file is None:
            sound_file = random.choice(sound_files)
        elif sound_file not in sound_files:
            await self._send_error(ctx, f"Sound file '{sound_file}' not found.")
            logging.error(f"Requested sound file not found: {sound_file}")
            return

        current_size = len(await self.get_queue_from_nickname())
        new_size = min(current_size + count, 1000)  # Limit the queue size to 1000
        logging.info(f"Adding {count} to queue. Old size: {current_size}, New size: {new_size}")
        await self.update_queue_size(new_size)

        if not self.is_playing:
            logging.info("Starting playback process")
            self.bot.loop.create_task(self._process_queue(ctx))
        else:
            await ctx.send(f"Added {count} song(s) to the queue. Current queue size: {new_size}")
            logging.info(f"Added {count} song(s) to the queue. Current queue size: {new_size}")

    async def _process_queue(self, ctx):
        self.is_playing = True
        while True:
            queue = await self.get_queue_from_nickname()
            if not queue:
                logging.info("Queue is empty, stopping playback")
                break
            
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                logging.info("Voice client disconnected, attempting to reconnect")
                try:
                    if ctx.author.voice:
                        await ctx.author.voice.channel.connect()
                        logging.info("Successfully reconnected to voice channel")
                    else:
                        logging.error("Author is not in a voice channel, cannot reconnect")
                        break
                except Exception as e:
                    logging.error(f"Failed to reconnect to voice channel: {str(e)}")
                    break

            sound_files = await self.get_sound_files()
            if not sound_files:
                await self._send_error(ctx, "No sound files found in the sounds directory.")
                logging.error("No sound files found in the sounds directory")
                break

            sound_file = random.choice(sound_files)
            new_size = len(queue) - 1
            logging.info(f"Playing sound file: {sound_file}. Updating queue size to {new_size}")
            await self.update_queue_size(new_size)
            
            try:
                source = discord.FFmpegPCMAudio(os.path.join(self.sound_dir, sound_file))
                if ctx.voice_client and ctx.voice_client.is_connected():
                    ctx.voice_client.play(source, after=lambda e: logging.error(f'Player error: {e}') if e else None)
                    logging.info(f"Started playing: {sound_file}")
                    
                    await self.api_call(self.bot.change_presence(activity=discord.Game(name=sound_file)))

                    # Wait for the audio to finish or for a disconnection
                    disconnect_check_interval = 1  # Check for disconnection every second
                    while ctx.voice_client and ctx.voice_client.is_playing():
                        await asyncio.sleep(disconnect_check_interval)
                        if not ctx.voice_client or not ctx.voice_client.is_connected():
                            logging.info("Disconnected while playing, stopping playback")
                            break

                    if ctx.voice_client and ctx.voice_client.is_connected():
                        logging.info(f"Finished playing: {sound_file}")
                    else:
                        logging.info("Playback interrupted due to disconnection")
                        break  # Exit the loop if disconnected

                    delay = random.randint(1, 10)
                    logging.info(f"Waiting for {delay} seconds before next song")
                    await asyncio.sleep(delay)
                else:
                    logging.error("Voice client is not connected when trying to play")
                    break
            except Exception as e:
                logging.error(f"Error during playback: {str(e)}")
                await asyncio.sleep(5)  # Wait a bit before trying the next song

        self.is_playing = False
        await self.api_call(self.bot.change_presence(activity=None))
        logging.info("Finished processing queue")

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        """Skip the current playing sound"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await self._send_error(ctx, "Nothing is currently playing.")

    @commands.command(aliases=['cq'])
    async def clear_queue(self, ctx):
        """Clear the sound queue"""
        await self.update_queue_size(0)
        await ctx.send("Queue cleared.")

    @commands.command(aliases=['sq'])
    async def show_queue(self, ctx):
        """Show the current sound queue"""
        queue = await self.get_queue_from_nickname()
        if not queue:
            await ctx.send("The sound queue is empty.")
        else:
            queue_size = len(queue)
            await ctx.send(f"Current queue size: {queue_size}")

    @commands.command(aliases=['ls'])
    async def list_sounds(self, ctx):
        """List all available sound files"""
        sound_files = await self.get_sound_files()
        if not sound_files:
            await self._send_error(ctx, "No sound files found in the sounds directory.")
            return
        
        file_list = "\n".join(sound_files)
        await self.api_call(ctx.send(f"Available sound files:\n```\n{file_list}\n```"))

    @commands.command(aliases=['rp'])
    async def random_play(self, ctx, count: int = 1):
        """Add a number of random sound files to the queue"""
        await self._add_random_to_queue(ctx, count)

    @app_commands.command(name="random_play", description="Add random sound file(s) to the queue")
    async def random_play_slash(self, interaction: discord.Interaction, count: int = 1):
        await self._add_random_to_queue(interaction, count)

    async def _add_random_to_queue(self, ctx_or_interaction, count: int = 1):
        if isinstance(ctx_or_interaction, discord.Interaction):
            await self.api_call(ctx_or_interaction.response.defer(ephemeral=True))
            ctx = await self.bot.get_context(ctx_or_interaction)
        else:
            ctx = ctx_or_interaction

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice:
                try:
                    await self.api_call(ctx.author.voice.channel.connect())
                except Exception as e:
                    await self._send_error(ctx, f"Failed to connect to voice channel: {str(e)}")
                    return
            else:
                await self._send_error(ctx, "You need to be in a voice channel to use this command.")
                return

        sound_files = await self.get_sound_files()
        if not sound_files:
            await self._send_error(ctx, "No sound files found in the sounds directory.")
            return

        current_size = len(await self.get_queue_from_nickname())
        new_size = min(current_size + count, 1000)  # Limit the queue size to 1000
        logging.info(f"Adding {count} random sounds to queue. Old size: {current_size}, New size: {new_size}")
        await self.update_queue_size(new_size)

        if not self.is_playing and ctx.voice_client and ctx.voice_client.is_connected():
            await self._process_queue(ctx)
        else:
            await ctx.send(f"Added {count} random sound(s) to the queue. Current queue size: {new_size}")

    async def _send_error(self, ctx, message):
        if isinstance(ctx, discord.Interaction):
            await self.api_call(ctx.followup.send(message, ephemeral=True))
        else:
            await self.api_call(ctx.send(message))

async def setup(bot):
    await bot.add_cog(Jukebox(bot))