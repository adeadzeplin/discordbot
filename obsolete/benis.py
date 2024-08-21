from discord.ext import commands

class Benis(commands.Cog):
    def __init__(self,client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Misc Loaded')
        # TODO: Replace hardcoded server and role IDs with environment variables or configuration file
        self.guild = self.client.get_guild(insert_your_server_id_here)
        self.role = self.guild.get_role(insert_your_role_id_here)  # benis role

    @commands.command()
    async def benis(self,ctx,target=None):
        # TODO: Implement error handling for invalid user targets
        # TODO: Add permission checks to restrict who can use this command
        if target != None:
            temp = int(target.strip('<!@>'))
            user = self.client.get_user(temp)
        else:
            user = ctx.message.author
        if ctx.guild == self.guild:
            await self.purgerole(self.role)
            await self.giveuserole(user,self.role)

    async def purgerole(self,role):
        # TODO: Implement error handling for role removal failures
        # TODO: Consider using bulk role updates for better performance
        for rolemember in role.members:
            await rolemember.remove_roles(role)

    async def giveuserole(self,user,role):
        # TODO: Implement error handling for role assignment failures
        # TODO: Consider optimizing this loop to avoid iterating through all guild members
        for mem in self.guild.members:
            if user == mem:
                await mem.add_roles(role)
                # TODO: Replace print statements with proper logging
                print(f"{mem} received {role}")

def setup(client):
    # TODO: Update this function to use the new async setup method
    client.add_cog(Benis(client))

# TODO: Add docstrings to all methods explaining their purpose and parameters
# TODO: Implement logging throughout the cog for better debugging and monitoring
# TODO: Consider adding a cooldown to the benis command to prevent spam
# REVIEW: Evaluate the purpose and potential misuse of this cog, and consider implementing safeguards