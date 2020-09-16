import discord
from discord.ext import tasks, commands
import asyncio
import os
import time
import numpy as np
import insult

class Goof(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.exemptmembers = []
        self.activeguildlist = []
        # self.roleids = [754794032542253216,754794032542253216]
        self.rolelist = []
        self.guild = None

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(.5)

        self.guild = self.client.get_guild(437778883744628736)
        print(f'Goof Loaded')
        await self.togglegoof()


    @tasks.loop(seconds=60*60)
    async def looping(self):

        #  754071294567514236 insult role for homies
        #  754794032542253216 test role
        rolee = self.guild.get_role(754071294567514236)
        await rolee.edit(name=f"The {insult.insult(formated=False,adjmax=1)}")

        for role in self.guild.roles:
            if role == rolee:
                await self.purgerole( role)
                await self.addmembertorole(role)




    @commands.command(aliases = ['g'] )
    async def togglegoof(self):
        # print(ctx.guild.get_role(754794032542253216))
        # role = ctx.guild.get_role(754071294567514236)

        if self.guild not in self.activeguildlist:
            self.activeguildlist.append(self.guild)
            self.looping.start()
            print("goof loop starting")

        # else:
        #     for i,x in enumerate(self.activeguildlist):
        #         if self.guild == i:
        #             self.activeguildlist.pop(x)
        #             break
        #
        #     self.looping.stop()
        #     print("goof loop stopping")


    async def purgerole(self,role): # Removes every member from a given role
        for rolemember in role.members:
            self.exemptmembers.append(rolemember)
            await rolemember.remove_roles(role)
            print(f"{rolemember} is no longer {role}")



    async def addmembertorole(self,role): # Gives a random member a role
        # for rolemember in role.members:
        if len(self.exemptmembers) < len(self.guild.members):
            flag = True
            rngperson = 0
            counter = 0
            while(flag):
                counter+=1
                if counter == 100:
                    return
                rngperson = np.random.randint(0,len(self.guild.members))
                if self.guild.members[rngperson] not in self.exemptmembers :
                    if self.guild.members[rngperson].mobile_status.name == 'online' or self.guild.members[rngperson].status.name == 'online':
                        flag = False
            await self.guild.members[rngperson].add_roles(role)
            print(f"{self.guild.members[rngperson]} received {role}")
        else:
            self.exemptmembers = []
            print("exempt is full")
            await self.addmembertorole(self, role)




        # temp = self.client.get_role(754794032542253216)
        # if temp in  ctx.guild.roles:
        #     print(temp)

        # try:
        #     self.do_bbb.start(ctx)
        #     await ctx.send(f"Comensing Operation nonsense")
        # except:
        #     await ctx.send(f"Operation nonsense is aleady in effect")


def setup(client):
    client.add_cog(Goof(client))