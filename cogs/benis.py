from discord.ext import commands

class Benis(commands.Cog):
    def __init__(self,client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Misc Loaded')
        self.guild = self.client.get_guild(437778883744628736)
        self.role = self.guild.get_role(757721456057516073)  # benis role

    @commands.command()
    async def benis(self,ctx,target=None):
        if target != None:
            temp = int(target.strip('<!@>'))
            user = self.client.get_user(temp)
        else:
            user = ctx.message.author
        if ctx.guild == self.guild:
            await self.purgerole(self.role)
            await self.giveuserole(user,self.role)

    async def purgerole(self,role): # Removes every member from a given role
        for rolemember in role.members:
            await rolemember.remove_roles(role)

    async def giveuserole(self,user,role):
        for mem in self.guild.members:
            if user == mem:
                await mem.add_roles(role)
                print(f"{mem} received {role}")

def setup(client):
    client.add_cog(Benis(client))