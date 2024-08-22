# RUN THIS FILE TO START THE BOT

import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import sys
import traceback

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.members = True

# Setup logging
log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, 'discord_bot.log')

logger = logging.getLogger('discord_bot')
logger.setLevel(logging.DEBUG)  # Change to DEBUG to capture more information

# File Handler
file_handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Redirect all uncaught exceptions to the log file
def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = exception_handler

# Disable other loggers
logging.getLogger('discord').setLevel(logging.ERROR)
logging.getLogger('discord.http').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)

class CustomBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.logger = logger

    async def setup_hook(self):
        self.logger.info("Bot is starting...")
        await self.load_cogs()

    async def load_cogs(self):
        initial_extensions = ['cogs.custom_help', 'cogs.misc', 'cogs.admin', 'cogs.bbb']
        for cog in initial_extensions:
            await self.load_extension(cog)

    async def on_ready(self):
        self.logger.info(f"Bot logged in as : {self.user}")
        self.logger.info("------")
        for cog in self.cogs:
            self.logger.info(f"{cog.capitalize()} Loaded")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            self.logger.error(f'In {ctx.command.qualified_name}:')
            self.logger.error(f'{original.__class__.__name__}: {str(original)}')
            self.logger.error(''.join(traceback.format_tb(original.__traceback__)))
        else:
            self.logger.error(f'In {ctx.command.qualified_name}:')
            self.logger.error(f'{error.__class__.__name__}: {str(error)}')

client = CustomBot()

def run_discordbot(p=None):
    if p:
        client.pipes = p
    try:
        client.run(TOKEN, log_handler=None)
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    run_discordbot()