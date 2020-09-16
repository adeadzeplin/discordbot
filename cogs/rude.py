import discord
from discord.ext import commands
from insult import insult
import insultdatabase
import asyncio



class Rude(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Rude Loaded')

    @commands.command(name='insult',help=': randomly generates an insult',aliases=['Insult','INSULT','i','I'])
    async def insultuser(self,ctx,*,InsultTarget="ctx.message.author"):
        await ctx.channel.purge(limit=1)

        if InsultTarget == "ctx.message.author":
            InsultTarget = ctx.message.author

        botnames = ['<@!725508807077396581>',
                    'e-bot',
                    'E-bot',
                    'ebot',
                    'Ebot'
                    ]
        if InsultTarget in botnames:
            await ctx.channel.send(':eyes:')
            await asyncio.sleep(3)
            await ctx.channel.purge(limit=1)
            response = f"{ctx.message.author} Insult me yourself you *dumb fucking coward*"
        else:

            response = str(InsultTarget) + " is " + insult()
        print(f"{ctx.message.author} insulted {InsultTarget}")

        await ctx.send(response)
    @commands.check_any(commands.is_owner())
    @commands.command(name='add_insult_noun', aliases=['ain','addinsultnoun'],help=': command to add new noun to database')
    async def addnoun(self,ctx, newnoun):
        print(f"{ctx.message.author} attempted to add the word {newnoun} to the database")
        response = insultdatabase.verify_new_noun(newnoun)
        await ctx.send(response)

    @commands.check_any(commands.is_owner())
    @commands.command(name='add_insult_adj', aliases=['aia','addinsultadj'],help=': command to add new adjective to database')
    async def addadj(self,ctx, newadj):
        print(f"{ctx.message.author} attempted to add the word {newadj} to the database")
        response = insultdatabase.verify_new_adj(newadj)
        await ctx.send(response)

    @commands.check_any(commands.is_owner())
    @commands.command(name='show_insult_db', help=": command to see what's in the database")
    async def showinsultdb(self,ctx):
        print(f"{ctx.message.author} requested to see the database")
        response = insultdatabase.printoutDB()
        await ctx.send(response)

def setup(client):
    client.add_cog(Rude(client))