import discord
from discord.ext import commands
from insult import insult
def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        print(f"{ctx.message.author} attempted something and caused an error {error}")
        if error.args[0] == "You do not have permission to run this command.":
            response = "Get fucked " + str(ctx.message.author) +"! You're " + insult() +". "+ error.args[0]
            await ctx.send(response)
        else:
            await ctx.send(f"I don't know what your trying do. {error}")

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def only_for_owners(self,ctx):
        await ctx.send("Man fuck you, I'll see you at work")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Admin Loaded')

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def load(self,ctx, extension):
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send(f"Loaded cog: {extension}")

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def unload(self, ctx, extension):
        self.client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unoaded cog: {extension}")

    @commands.command(aliases = ['r'])
    @commands.check_any(commands.is_owner())
    async def reload(self, ctx, extension):
        self.client.unload_extension(f"cogs.{extension}")
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send(f"Reloaded cog: {extension}")

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def clear(self, ctx, num=1):
        await ctx.channel.purge(limit=num)
        print(f'Bot removed {num} from the channel: {ctx.channel.name}')


    @commands.command()
    @commands.check_any(commands.is_owner())
    async def req(self, ctx, *,request):
        import importlib.util
        spec = importlib.util.spec_from_file_location("searchsheet", 'C:/Users/smithdepazd/PycharmProjects/olgabot/searrchsheet.py')
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        for index in foo.searchsheet(request):

            await ctx.send(f"{index}")
        await ctx.send(f"That's everything i could find")

def setup(client):
    client.add_cog(Admin(client))