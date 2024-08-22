import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
# import  sounddevice as sd
# from insult import insult
# import insultdatabase
import random
import os
from dotenv import load_dotenv
from discord.ext import tasks

load_dotenv()
botit = os.getenv('BOT_ID')

class Misc(commands.Cog):
    """Miscellaneous commands for various purposes."""

    def __init__(self, client):
        self.client = client
        # TODO: Consider adding a setup method to initialize any necessary attributes

    @commands.Cog.listener()
    async def on_ready(self):
        # self.client.logger.info('Misc Loaded')
        # TODO: Replace print statement with proper logging
        pass

    @commands.command(name='invite', help='Generates a link to invite the bot to a server')
    async def invitebot(self, ctx):
        """Generate an invite link for the bot.
        
        Usage: !invite
        """
        # TODO: Consider moving the oauth_url generation to a separate utility function
        response = discord.utils.oauth_url(botit, permissions=None, guild=None, redirect_uri=None)
        await ctx.send(response)
        # TODO: Add error handling for oauth_url generation and message sending

    def returnlist(self, list, lerst):
        # REVIEW: Consider renaming this method to be more descriptive
        output = ''
        for l in list:
            if l in lerst:
                output += l + ' '
        return output
        # TODO: Consider combining returnlist and checklist methods into a single utility method

    def checklist(self, list, lerst):
        # REVIEW: Consider renaming this method to be more descriptive
        for l in list:
            if l in lerst:
                return True
        return False
        # TODO: Consider combining returnlist and checklist methods into a single utility method

    @commands.Cog.listener()
    async def on_message(self, message):
        # TODO: Consider moving this list to a configuration file
        booey = ['booey','hoo','hooh','dub','baba','bababooey','bobby','benis','boofer','coochie','cunt','cease','why','ok','bruh','dude','pussy','later','when','uh',
                 'ew','gross','dood','<:NUT:671476999558135868>']
        if message.author != self.client.user:
            if message.content.startswith('!'):
                pass
            elif '<@725508807077396581>' in message.content:
                # TODO: Consider making this response configurable
                await message.channel.send(':eyes:')
                await asyncio.sleep(3)
                await message.channel.purge(limit=2)
                # TODO: Implement rate limiting for bot mentions to prevent spam

    @commands.command(name='ping', help='Check the bot\'s latency')
    async def ping(self, ctx):
        """Check the bot's latency.
        
        Usage: !ping
        """
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')



    # TODO: Implement a method to handle configuration reloading
    # TODO: Add more utility commands such as server info, user info, etc.

    # TODO: Add more utility commands that could be useful for server management
    # REVIEW: Consider implementing a custom help command for better usability
    # TODO: Implement comprehensive error handling for all commands
    # REVIEW: Evaluate the necessity of each imported module
    # TODO: Add docstrings to all methods explaining their purpose and parameters

async def setup(client):
    await client.add_cog(Misc(client))
# OVERALL NOTES:
# TODO: Implement logging for better debugging and monitoring
# REVIEW: Consider breaking this cog into smaller, more focused cogs if it grows larger
# TODO: Implement rate limiting to prevent command spam
# REVIEW: Consider adding unit tests for the cog's functionality