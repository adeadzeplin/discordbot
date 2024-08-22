import discord
from discord.ext import commands
import random
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomHelpCommand(commands.HelpCommand):
    """A custom help command to provide detailed information about bot commands."""
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
            description="Use the buttons below to navigate through cmd categories:",
            color=self.color
        )
        
        category_embeds = {}
        
        for cog, cmds in mapping.items():
            if cog and cog.qualified_name.lower() == "help":
                continue  # Skip the Health category
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                cog_name = cog.qualified_name if cog else "Miscellaneous"
                cog_description = cog.description if cog and cog.description else "No description available"
                main_embed.add_field(
                    name=cog_name,
                    value=f"{cog_description}\n{len(filtered)} cmd(s)",
                    inline=False
                )
                
                category_embed = discord.Embed(
                    title=f"{cog_name} Commands",
                    description=cog_description,
                    color=self.get_random_color()
                )
                for cmd in filtered:
                    admin_only = any('is_owner' in check.__qualname__ for check in cmd.checks if hasattr(check, '__qualname__'))
                    description = cmd.short_doc or 'No description'
                    if admin_only:
                        description += "\n**[Admin Only]**"
                    category_embed.add_field(
                        name=f"{self.context.clean_prefix}{cmd.name}",
                        value=f"{description}\n"
                              f"Usage: `{self.get_command_signature(cmd)}`",
                        inline=False
                    )
                category_embeds[cog_name] = category_embed

        main_embed.set_footer(text=f"Use '{ctx.prefix}help <cmd>' for more info on a specific cmd.")
        view = HelpView(self.context, main_embed, category_embeds)
        message = await self.context.send(embed=main_embed, view=view)
        view.message = message

    async def send_command_help(self, cmd):
        embed = discord.Embed(
            title=f"Help: {cmd.name}",
            description=cmd.help or "No detailed help available.",
            color=self.color
        )
        embed.add_field(name="Usage", value=f"`{self.get_command_signature(cmd)}`", inline=False)
        if cmd.aliases:
            embed.add_field(name="Aliases", value=", ".join(cmd.aliases), inline=False)
        
        admin_only = any('is_owner' in check.__qualname__ for check in cmd.checks if hasattr(check, '__qualname__'))
        if admin_only:
            embed.add_field(name="Permissions", value="**Admin Only**", inline=False)
        
        embed.set_footer(text=f"Category: {cmd.cog_name or 'No Category'}")
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=str(error), color=discord.Color.red())
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
            self.add_item(CategoryButton(category, self.category_embeds[category]))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This menu is not for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Main Menu", style=discord.ButtonStyle.secondary, row=1)
    async def main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.main_embed)

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

class CategoryButton(discord.ui.Button):
    def __init__(self, label, embed):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.embed = embed

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embed)

class Help(commands.Cog):
    """Provides help and information about bot commands."""
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

async def setup(bot):
    await bot.add_cog(Help(bot))