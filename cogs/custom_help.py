import discord
from discord.ext import commands
import random
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.color = discord.Color.blue()
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 3, commands.BucketType.user)

    def get_random_color(self):
        return discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    async def send_bot_help(self, mapping):
        ctx = self.context
        bucket = self.cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return await ctx.send(f"Slow down! Try again in {retry_after:.1f} seconds.", delete_after=5)

        main_embed = discord.Embed(
            title="Bot Commands Overview",
            description="Use the buttons below to navigate through command categories:",
            color=self.color
        )
        
        category_embeds = {}
        
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                cog_name = cog.qualified_name if cog else "Miscellaneous"
                cog_description = cog.description if cog and cog.description else "No description available"
                main_embed.add_field(
                    name=cog_name,
                    value=f"{cog_description}\n{len(filtered)} command(s)",
                    inline=False
                )
                
                category_embed = discord.Embed(
                    title=f"{cog_name} Commands",
                    description=cog_description,
                    color=self.get_random_color()
                )
                for command in filtered:
                    admin_only = any('is_owner' in check.__qualname__ for check in command.checks if hasattr(check, '__qualname__'))
                    description = command.short_doc or 'No description'
                    if admin_only:
                        description += "\n**[Admin Only]**"
                    category_embed.add_field(
                        name=f"{self.context.clean_prefix}{command.name}",
                        value=f"{description}\n"
                              f"Usage: `{self.get_command_signature(command)}`",
                        inline=False
                    )
                category_embeds[cog_name] = category_embed

        main_embed.set_footer(text="Use '!help <command>' for more info on a command.")
        view = HelpView(self.context, main_embed, category_embeds)
        await self.context.send(embed=main_embed, view=view)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Help: {command.name}",
            description=command.help or "No detailed help available.",
            color=self.color
        )
        embed.add_field(name="Usage", value=f"`{self.get_command_signature(command)}`", inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        
        admin_only = any('is_owner' in check.__qualname__ for check in command.checks if hasattr(check, '__qualname__'))
        if admin_only:
            embed.add_field(name="Permissions", value="**Admin Only**", inline=False)
        
        embed.set_footer(text=f"Category: {command.cog_name or 'No Category'}")
        await self.get_destination().send(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, ctx, main_embed, category_embeds):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.main_embed = main_embed
        self.category_embeds = category_embeds
        self.message = None
        self.add_category_buttons()

    def add_category_buttons(self):
        for category in self.category_embeds.keys():
            self.add_item(CategoryButton(category))

    @discord.ui.button(label="Main Menu", style=discord.ButtonStyle.secondary, row=4)
    async def main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.main_embed)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This help menu is not for you.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

class CategoryButton(discord.ui.Button):
    def __init__(self, category):
        super().__init__(style=discord.ButtonStyle.primary, label=category, custom_id=category)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if self.custom_id in view.category_embeds:
            await interaction.response.edit_message(embed=view.category_embeds[self.custom_id])

class Help(commands.Cog):
    """Provides help and information about bot commands."""
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

async def setup(bot):
    # logger.debug("Setting up CustomHelpCommand")
    try:
        help_cog = Help(bot)
        await bot.add_cog(help_cog)
        # logger.debug("CustomHelpCommand setup complete")
    except Exception as e:
        logger.error(f"Error setting up CustomHelpCommand: {str(e)}")
        raise