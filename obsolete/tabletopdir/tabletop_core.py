import discord
from discord.ext import commands
import asyncio

class SimpleView(discord.ui.View):

    foo: bool = None


    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)


    async def on_timeout(self) -> None:
        await self.message.channel.send("Timedout")
        await self.disable_all_items()


    @discord.ui.button(label="Hello",
                       style=discord.ButtonStyle.success)
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("World")
        self.foo = True
        self.stop()


    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling")
        self.foo = False
        self.stop()