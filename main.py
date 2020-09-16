# bot.py Is the main bot file
# do not run this file

import os
import random
from insult import insult
from discord.ext import commands
from dotenv import load_dotenv
import discord
import insultdatabase

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Bot logged in as : {bot.user.name}')
    print(bot.user.id)
    print('------')


@bot.command()
async def clear(ctx):
    print(f'Bot removed everything in the channel: {ctx.channel.name}')
    await ctx.channel.purge()

@bot.command(name='insult',help=': generates insult in the form of "Blah blah is a bad thing',aliases=['Insult','INSULT'])
async def insultuser(ctx,*,InsultTarget):
    print(f"{ctx.message.author} insulted {InsultTarget}")
    response = str(InsultTarget) + " is " + insult()
    await ctx.send(response)

@bot.command(name='direct_insult',help=': generates insult in the form of "Blah blah is a bad thing')
async def insultuser(ctx,InsultTarget):


    print(f"{ctx.message.author} directly insulted {InsultTarget}")
    response = str(InsultTarget) + " is " + insult()
    await ctx.send(response)

@bot.command(name='add_insult_noun',help=': command to add new noun to database. No spaces allowed')
async def insultuser(ctx,newnoun):
    print(f"{ctx.message.author} attempted to add the word {newnoun} to the database")
    response = insultdatabase.verify_new_noun(newnoun)
    await ctx.send(response)


@bot.command(name='add_insult_adj',help=': command to add new adjective to database. No spaces allowed')
async def insultuser(ctx,newadj):
    print(f"{ctx.message.author} attempted to add the word {newadj} to the database")
    response = insultdatabase.verify_new_adj(newadj)
    await ctx.send(response)


@bot.command(name='show_insult_db',help=": command to see what's in the database. No spaces allowed")
async def insultuser(ctx):
    print(f"{ctx.message.author} requested to see the database")

    response = insultdatabase.printoutDB()
    await ctx.send(response)

@bot.command(name='invite',help=': generates link to invite bot')
async def invitebot(ctx):
    response = discord.utils.oauth_url(725091184464232528, permissions=None, guild=None, redirect_uri=None)
    await ctx.send(response)


bot.run(TOKEN)

