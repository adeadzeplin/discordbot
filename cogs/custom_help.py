from discord.ext import commands
import discord

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Bot Commands", description="Here's a list of available commands:", color=0x00ff00)
        
        for cog, commands in mapping.items():
            command_list = [f"`{command.name}`" for command in commands if not command.hidden]
            if command_list:
                embed.add_field(name=cog.qualified_name if cog else "No Category", value=", ".join(command_list), inline=False)
        
        embed.set_footer(text="Type !help <command> for more info on a specific command.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Help: {command.name}", description=command.help or "No description available.", color=0x00ff00)
        embed.add_field(name="Usage", value=f"`!{command.name} {command.signature}`")
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases))
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f"{cog.qualified_name} Commands", description=cog.description or "No description available.", color=0x00ff00)
        for command in cog.get_commands():
            embed.add_field(name=command.name, value=command.help or "No description available.", inline=False)
        await self.get_destination().send(embed=embed)

class Help(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

async def setup(bot):
    await bot.add_cog(Help(bot))

# TODO: Ensure all commands have proper help text and usage information
# REVIEW: Consider categorizing commands for easier navigation
# TODO: Implement permission checks to show only commands the user can access
# TODO: Add examples for each command in the help text
