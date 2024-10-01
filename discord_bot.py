import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import asyncio
import datetime
from typing import List, Dict

# Load environment variables
load_dotenv()

# Set up logging
def setup_logging():
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, 'discord_bot.log')
    
    # Clear the log file
    with open(log_file, 'w') as f:
        f.write(f"Log file cleared on {datetime.datetime.now()}\n")

    # Set up rotating file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Call setup_logging at the start
setup_logging()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')
    print(f'{bot.user} is ready and connected to Discord!')
    
    # Sync application commands
    await bot.tree.sync()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Sync application commands"""
    synced = await bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} commands.")

@bot.tree.command(name="ping", description="Check bot's latency")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(bot.latency * 1000)}ms")

# Replace the existing help command setup with:
class SimpleHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="ebot Help", description="Here are all available commands:", color=discord.Color.blue())
        
        for cog, cmds in mapping.items():
            cog_name = getattr(cog, "qualified_name", "No Category")
            command_list = [cmd for cmd in cmds if not cmd.hidden]
            
            if command_list:
                command_value = ""
                for cmd in command_list:
                    aliases = ", ".join(cmd.aliases) if cmd.aliases else "None"
                    command_value += f"`{cmd.name}` (Aliases: {aliases})\n"
                embed.add_field(name=cog_name, value=command_value, inline=False)
        
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Help for {command.name}", color=discord.Color.green())
        embed.add_field(name="Description", value=command.help or "No description available", inline=False)
        embed.add_field(name="Usage", value=f"`{self.get_command_signature(command)}`", inline=False)
        aliases = ", ".join(command.aliases) if command.aliases else "None"
        embed.add_field(name="Aliases", value=aliases, inline=False)
        
        channel = self.get_destination()
        await channel.send(embed=embed)

# Replace the existing help command setup with:
bot.help_command = SimpleHelpCommand()

# Load cogs
initial_extensions = ['cogs.jukebox', 'cogs.admin', 'cogs.cocophany']  # Added 'cogs.cocophany'

async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            logging.info(f"Successfully loaded extension: {extension}")
            print(f"Successfully loaded extension: {extension}")
        except Exception as e:
            logging.error(f"Failed to load extension {extension}: {str(e)}")
            print(f"Failed to load extension {extension}: {str(e)}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv('DISCORD_TOKEN'))

# Run the bot
if __name__ == '__main__':
    asyncio.run(main())