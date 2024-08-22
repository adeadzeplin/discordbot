import discord
from discord.ext import commands
import asyncio

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

class Admin(commands.Cog):
    """Administrative commands for bot management."""
    def __init__(self,client):
        self.client = client

    @commands.command(help="Owner-only command", brief="Owner-only command")
    @commands.check_any(commands.is_owner())
    async def only_for_owners(self,ctx):
        await ctx.send("This command can only be used by the bot owner.")

    @commands.command(help="Load a cog extension", brief="Load cog")
    @commands.check_any(commands.is_owner())
    async def load(self,ctx, extension):
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send(f"Loaded cog: {extension}")

    @commands.command(help="Unload a cog extension", brief="Unload cog")
    @commands.check_any(commands.is_owner())
    async def unload(self, ctx, extension):
        self.client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unloaded cog: {extension}")

    @commands.command(aliases=['r'], help="Reload a cog extension", brief="Reload cog")
    @commands.check_any(commands.is_owner())
    async def reload(self, ctx, extension):
        self.client.unload_extension(f"cogs.{extension}")
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send(f"Reloaded cog: {extension}")

    @commands.command(help="Clear a specified number of messages", brief="Clear messages")
    @commands.check_any(commands.is_owner())
    async def clear(self, ctx, num=1):
        """Clear a specified number of messages from the channel.
        
        Usage: !clear [number]
        Example: !clear 5
        
        [number] - Optional: Number of messages to clear (default: 1)
        """
        await ctx.channel.purge(limit=num+1)

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def req(self, ctx, *,request):
        """Execute a custom request (admin only).
        
        Usage: !req <request>
        Example: !req update_database
        
        <request> - The custom request to execute
        """
        # TODO: Consider moving this import to the top of the file
        import importlib.util
        # TODO: Use a configuration file or environment variable for file paths
        spec = importlib.util.spec_from_file_location("searchsheet", 'C:/Users/smithdepazd/PycharmProjects/olgabot/searrchsheet.py')
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        # TODO: Implement error handling for search failures
        for index in foo.searchsheet(request):
            await ctx.send(f"{index}")
        await ctx.send(f"That's everything i could find")

    @commands.Cog.listener()
    async def on_ready(self):
        # self.client.logger.info('Admin Loaded')
        pass

async def setup(client):
    await client.add_cog(Admin(client))