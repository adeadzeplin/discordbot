import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        """Reload a cog"""
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"Cog {cog} has been reloaded.")
        except Exception as e:
            await ctx.send(f"Error reloading cog {cog}: {str(e)}")

    async def cog_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=cog, value=cog)
            for cog in self.bot.cogs if current.lower() in cog.lower()
        ]

    @app_commands.command(name="reload_cog", description="Reload a cog (Admin only)")
    @app_commands.autocomplete(cog=cog_autocomplete)
    @app_commands.check(lambda interaction: interaction.user.id == interaction.client.owner_id)
    async def reload_slash(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"Cog {cog} has been reloaded.")
        except Exception as e:
            await interaction.response.send_message(f"Error reloading cog {cog}: {str(e)}")

async def setup(bot):
    await bot.add_cog(Admin(bot))