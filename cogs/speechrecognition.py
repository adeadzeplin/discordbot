import discord
from discord.ext import commands
import speech_recognition as sr
import asyncio
import logging
from discord import app_commands
from typing import List
import io
import wave

class SpeechRecognition(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I'm not connected to a voice channel.")

    @commands.command()
    async def listen(self, ctx):
        if not ctx.voice_client:
            await ctx.send("I'm not connected to a voice channel. Use !join first.")
            return

        self.logger.info("Attempting to record audio...")
        
        try:
            # Create a sink to receive audio data
            sink = discord.sinks.WaveSink()
            
            # Start recording
            ctx.voice_client.start_recording(sink, self.finished_callback, ctx)
            
            await ctx.send("Listening... Say something!")
            
            # Record for 5 seconds
            await asyncio.sleep(5)
            
            # Stop recording
            ctx.voice_client.stop_recording()
        except AttributeError:
            self.logger.error("Error: discord.sinks is not available. Make sure you're using the latest version of discord.py")
            await ctx.send("An error occurred while trying to listen. The bot might not support audio recording.")
        except Exception as e:
            self.logger.error(f"Error during recording: {str(e)}")
            await ctx.send("An error occurred while trying to listen.")

    async def finished_callback(self, sink, ctx):
        self.logger.info("Finished recording audio.")
        
        recorded = sink.audio_data
        if not recorded:
            await ctx.send("No audio was recorded.")
            return
        
        # Get the first (and only) recorded user
        user_id, audio = next(iter(recorded.items()))
        
        # Convert audio data to wav format
        wav_data = io.BytesIO(audio.file.getvalue())
        
        # Use speech recognition to convert audio to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_data) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                await ctx.send(f"Recognized speech: {text}")
            except sr.UnknownValueError:
                await ctx.send("Speech was not understood")
            except sr.RequestError as e:
                await ctx.send(f"Could not request results from speech recognition service; {e}")

async def setup(bot):
    await bot.add_cog(SpeechRecognition(bot))