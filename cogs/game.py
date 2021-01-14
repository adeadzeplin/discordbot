import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
# import  sounddevice as sd
from insult import insult
import insultdatabase
import random
import os
from dotenv import load_dotenv

load_dotenv()
botit = os.getenv('BOT_ID')


dice_emotes = [ '<:ds:785593289868312659>', '<:d1:785593289565929493>', '<:d2:785593289591488562>', '<:d3:785593289516253256>', '<:d4:785593289402875935>', '<:d5:785593289369845761>', '<:d6:785593289708797972>', '<:d7:785593289418997761>', '<:d8:785593289843539978>', '<:d9:785593289729638401>', '<:d10:785593289834889216>']
dice_o = '<:iso:785599417356124232>'

def rand_obj(lis):
    return lis[random.randint(0,len(lis)-1)]

class Player():
    def __init__(self,dude,dicelim,dicecount):
        self.dude = dude
        self.game_display = None
        self.dice_display = None
        self.status_display = None
        self.status_message = "Status:"
        self.dice = []
        for i in range(dicecount):
            self.dice.append(random.randint(0,dicelim))
    def roll(self,dicelim):
        for x,i in enumerate(self.dice):
            self.dice[x] = random.randint(0,dicelim)

class DiceGame():
    def __init__(self,category_withchannels_innit):
        self.category = category_withchannels_innit
        self.players = []
        self.ready_players = []
        self.dicelim = 6
        self.dicecount = 6
        self.player_turn_tracker = 0
        self.recent_bid = Noneh
        self.recent_bider= None
        self.state = None
        self.dice_commands = {
            'bid':self.bid,
            'spot': self.spot,
            'bluff':self.bluff
        }
    def next_turn(self):
        self.update_statuses_bid()
        self.player_turn_tracker +=1
        for i in self.players:
            if self.player_turn_tracker >= len(self.players):
                self.player_turn_tracker = 0
            if len(self.players[self.player_turn_tracker].dice) == 0:
                self.player_turn_tracker += 1
            else:
                return




    def update_statuses_bid(self):
        for p in self.players:
            if self.recent_bid[1] == 's':
                img = dice_emotes[0]
            else:
                img = dice_emotes[self.recent_bid[1]]
            if p == self.recent_bider:
                p.status_message = f"Status: **YOU** just bid that there are {self.recent_bid[0]} dice with the value of {img}"
            else:
                p.status_message = f"Status: {self.recent_bider.dude.nick} just bid that there are {self.recent_bid[0]} dice with the value of {img}"

    def valid_bid(self,count,value):
        self.recent_bider = self.players[self.player_turn_tracker]
        self.recent_bid = (count, value)
        self.update_statuses_bid()
        self.next_turn()

    async def bid(self,message,user_channel):
        msg = message.content.split(' ')
        if message.author.nick == self.players[self.player_turn_tracker].dude.nick:
            if len(msg) == 3:
                try:
                    count = int(msg[1])
                    if msg[2] in ['s','S']:
                        value = (msg[2])
                    else:
                        value = int(msg[2])
                except:
                    await user_channel.purge(limit=1)
                    print(f"{user_channel.name} mis-formated their bid with not numbers")

                    self.players[self.player_turn_tracker].status_message = "You typed your bid command wrong: bid (num_of_dice) (face_number)"
                    # await user_channel.send("You typed your bid command wrong: bid num_of_dice value_of_dice" + message.content)
                    await self.update_screens()
                    return
                print(f"DiceGameRUN: {message.content}")

                if count >= 1: # valid dice number
                    if self.recent_bid == None:
                        if value in ['s','S']:
                            self.valid_bid(count,value)

                        elif (value <= self.dicelim and value >= 1):
                            self.valid_bid(count, value)

                        else:
                            print(f"{user_channel.name} failed to formot a bid properly")
                            self.players[self.player_turn_tracker].status_message = f'ERROR: You Must either bid a valid bid'


                    elif value in ['s','S']:
                        if self.recent_bid[1] not in ['s','S']:
                            if count >= self.recent_bid[0]//2+1:
                                self.valid_bid(count, value)

                            else:
                                print(f"{user_channel.name} failed to bid a star on a number")
                                self.players[self.player_turn_tracker].status_message = f'ERROR: In order to bid a star you must bid at least half+1 of the current bid '

                        elif count > self.recent_bid[0]:
                            self.valid_bid(count, value)

                        else:
                            print(f"{user_channel.name} failed to bid something higher than the current bid")
                            self.players[self.player_turn_tracker].status_message = f'ERROR:You must bid a higher number of dice '

                    elif self.recent_bid[1] in ['s','S']:
                        if count >= self.recent_bid[0]*2+1:
                            self.valid_bid(count, value)
                        else:
                            print(f"{user_channel.name} failed to bid a number on a star")
                            self.players[self.player_turn_tracker].status_message = f'ERROR: In order to bid a number you must bid at least double+1 of the current bid '

                    elif (value <= self.dicelim and value >= 1):

                        if count >= self.recent_bid[0] and value > self.recent_bid[1]:
                            self.valid_bid(count,value)
                        elif count > self.recent_bid[0] and value >= self.recent_bid[1]:
                            self.valid_bid(count,value)
                        else:
                            print(f"{user_channel.name} failed to bid something higher than the current bid")

                            self.players[self.player_turn_tracker].status_message = f'ERROR: You Must either bid a higher number of dice or a higher dice face number'

                    else:
                        print(f"{user_channel.name} tried to bid an invalid dice face number")

                        self.players[self.player_turn_tracker].status_message = f'ERROR: Invalid Dice Face Number. Number must be between {1} and {self.dicelim} or S'
                else:
                    print(f"{user_channel.name} tried to bid less than one dice")

                    self.players[self.player_turn_tracker].status_message = f'ERROR: Invalid Number of dice. Number must be higher than the current bid or at least 1'
                await user_channel.purge(limit=1)
                await self.update_screens()
            else:
                # await user_channel.purge(limit=1)
                print(f"{user_channel.name} tried to bid but mis-formated the command")

                self.players[self.player_turn_tracker].status_message = "You typed your bid command wrong: bid (num_of_dice) (face_number)"
                await user_channel.purge(limit=1)
                await self.update_screens()

        else:
            for p in self.players:
                if p.dude.nick == message.author.nick:
                    print(f"{p.dude.nick} tried biding when it wasn't their turn")
                    p.status_message =f"ERROR: It is not your turn, You may not bid now"
                    await user_channel.purge(limit=1)
                    await self.update_screens()
                    break

    def checkdicebidspot(self):
        count = 0
        dice_bid = self.recent_bid[0]
        dice_face = self.recent_bid[1]
        if dice_face == 's':
            dice_face = 0
        for p in self.players:
            for d in p.dice:
                if d == dice_face or d == 0:
                    count += 1
        if dice_bid != count:
            return True , count
        return False, count

    def update_statuses_spot(self,result,callername):
        if self.recent_bid[1] in ['s','S']:
            diceshown = f"{dice_emotes[0]}"
        else:
            diceshown = f"either a {dice_emotes[self.recent_bid[1]]} or a {dice_emotes[0]}"
        # a = 'Status: '
        # you = '**YOU**'
        # b = ' called bluff on '

        inst = insult(adjmax=1)
        for p in self.players:
            if result[0]:
                if p.dude.nick == callername:
                    p.status_message = f"Status: **YOU** called Spot-on on {self.recent_bider.dude.nick}'s bid!\n The bid was {self.recent_bid[0]} dice that show {diceshown}\n **YOU** were Wrong! There are only {result[1]} dice. **YOU** lose a die for being {inst}."
                elif p == self.recent_bider:
                    p.status_message = f"Status: {callername} called Spot-on on **YOUR** bid!\nThe bid was {self.recent_bid[0]} dice that show {diceshown}\n **{callername}** was Wrong! There are only {result[1]} dice. {callername} loses a die for being {inst}."
                else:
                    p.status_message = f"Status: {callername} called Spot-on on {self.recent_bider.dude.nick}'s bid!\nThe bid was {self.recent_bid[0]} dice that show {diceshown}\n **{callername}** was Wrong! There are only {result[1]} dice. {callername} loses a die for being {inst}."

            else:
                if p.dude.nick == callername:
                    p.status_message = f"Status: **YOU** called Spot-on on {self.recent_bider.dude.nick}'s bid!\n There are {result[1]} of {diceshown} and the bid was {self.recent_bid[0]} dice\n **{self.recent_bider.dude.nick}** Lied! **{self.recent_bider.dude.nick}** loses a die for being {inst}."
                elif p == self.recent_bider:
                    p.status_message = f"Status: **{callername}** called Spot-on on **YOU**'s bid!\n There are {result[1]} of {diceshown} and the bid was {self.recent_bid[0]} dice\n **YOU** Lied! **YOU** loses a die for being {inst}."
                else:
                    p.status_message = f"Status: **{callername}** called Spot-on on {self.recent_bider.dude.nick}'s bid!\n There are {result[1]} of {diceshown} and the bid was {self.recent_bid[0]} dice\n **{self.recent_bider.dude.nick}** Lied! **{self.recent_bider.dude.nick}** loses a die for being {inst}."


    async def spot(self,message,user_channel):
        if self.recent_bider.dude.nick == None:
            for p in self.players:
                if p.dude.nick == message.author.nick:
                    p.status_message = f"You can't call spot on nothing. Stupid**.**"
        elif message.author.nick != self.recent_bider.dude.nick:
            flag = False
            for p in self.players:
                if p.dude.nick == message.author.nick:
                    if len(p.dice) != 0:
                        flag = True
                        break
            if flag:
                result = self.checkdicebidspot()
                if result[0]:  # If the spot call was wrong
                    for p in self.players:
                        if p.dude.nick == message.author.nick:  # punish the one who called it
                            p.dice.pop()
                            self.update_statuses_spot(result, message.author.nick)

                        p.roll(self.dicelim)
                else:  # if the bluf call was right
                    for p in self.players:
                        if p.dude.nick == self.recent_bider.dude.nick:  # punish the one who lied
                            p.dice.pop()
                            self.update_statuses_spot(result, message.author.nick)
                        p.roll(self.dicelim)

                self.recent_bider = None
                self.recent_bid = None
        await self.update_screens()
        await user_channel.purge(limit=1)

        # await user_channel.send("SPOT " + message.content)
    def checkdicebid(self):
        count = 0
        dice_bid = self.recent_bid[0]
        dice_face = self.recent_bid[1]
        if dice_face == 's':
            dice_face = 0
        for p in self.players:
            for d in p.dice:
                if d == dice_face or d == 0:
                    count += 1
        if dice_bid <= count:
            return True , count
        return False, count

    def update_statuses_bluff(self,result,callername):
        if self.recent_bid[1] in ['s','S']:
            diceshown = f"{dice_emotes[0]}"
        else:
            diceshown = f"either a {dice_emotes[self.recent_bid[1]]} or a {dice_emotes[0]}"
        # a = 'Status: '
        # you = '**YOU**'
        # b = ' called bluff on '

        inst = insult(adjmax=1)
        for p in self.players:
            if result[0]:
                if p.dude.nick == callername:
                    p.status_message = f"Status: **YOU** called bluff on {self.recent_bider.dude.nick}'s bid!\n There are {result[1]} dice that show {diceshown}\n **YOU** were Wrong! There are at least {self.recent_bid[0]} dice. **YOU** lose a die for being {inst}."
                elif p == self.recent_bider:
                    p.status_message = f"Status: {callername} called bluff on **YOUR** bid!\n There are {result[1]} dice that show {diceshown}\n **{callername}** was Wrong! There are at least {self.recent_bid[0]} dice. {callername} loses a die for being {inst}."
                else:
                    p.status_message = f"Status: {callername} called bluff on {self.recent_bider.dude.nick}'s bid!\n There are {result[1]} dice that show {diceshown}\n **{callername}** was Wrong! There are at least {self.recent_bid[0]} dice. {callername} loses a die for being {inst}."

            else:
                if p.dude.nick == callername:
                    p.status_message = f"Status: **YOU** called bluff on {self.recent_bider.dude.nick}'s bid!\n They claimed there are {self.recent_bid[0]} of {diceshown} when there were only {result[1]} \n **{self.recent_bider.dude.nick}** Lied! **{self.recent_bider.dude.nick}** loses a die for being {inst}."
                elif p == self.recent_bider:
                    p.status_message = f"Status: **{callername}** called bluff on **YOU**'s bid!\n **YOU** claimed there are {self.recent_bid[0]} of {diceshown} when there were only {result[1]} \n **YOU** Lied! **YOU** loses a die for being {inst}."
                else:
                    p.status_message = f"Status: **{callername}** called bluff on {self.recent_bider.dude.nick}'s bid!\n They claimed there are {self.recent_bid[0]} of {diceshown} when there were only {result[1]} \n **{self.recent_bider.dude.nick}** Lied! **{self.recent_bider.dude.nick}** loses a die for being {inst}."

            #     p.status_message = f"Status: {self.recent_bider.dude.nick} just bid that there are {self.recent_bid[0]} dice with the value of {img}"


    async def bluff(self,message,user_channel):
        if self.recent_bider.dude.nick == None:
            for p in self.players:
                if p.dude.nick == message.author.nick:
                    p.status_message = f"You can't call bluff on nothing. Stupid**.**"

        elif message.author.nick != self.recent_bider.dude.nick:
            flag = False
            for p in self.players:
                if p.dude.nick == message.author.nick:
                    if len(p.dice) != 0 :
                        flag = True
                        break
            if flag:
                result = self.checkdicebid()
                if result[0]: # If the bluf call was wrong
                    for p in self.players:
                        if p.dude.nick == message.author.nick: # punish the one who called it
                            p.dice.pop()
                            self.update_statuses_bluff(result,message.author.nick)

                        p.roll(self.dicelim)
                else:# if the bluf call was right
                    for p in self.players:
                        if p.dude.nick == self.recent_bider.dude.nick: # punish the one who lied
                            p.dice.pop()
                            self.update_statuses_bluff(result,message.author.nick)
                        p.roll(self.dicelim)

                self.recent_bider = None
                self.recent_bid = None
        await self.update_screens()
        await user_channel.purge(limit=1)

        # await user_channel.send("BLUFF " + message.content)

    def init_players(self,players):
        for p in players:
            self.players.append(Player(p,self.dicelim,self.dicecount))
            print(f"DiceGame init_Player: {p}")
        self.player_turn_tracker = random.randint(0,len(self.players)-1)
        print(f"DiceGame it's {self.players[self.player_turn_tracker].dude.nick}'s turn")

    async def run(self,message,user_channel):
        # if message.author == self.players[self.player_turn_tracker].dude.nick:
        if self.state == None:
            if message.author.nick == message.channel.name:
                if message.content.lower()=='ready':
                    if message.author not in self.ready_players:
                        self.ready_players.append(message.author)
                        for x,d in enumerate(self.players):
                            if d.dude.nick == message.author.nick:
                                if self.players[x].game_display == None:
                                    await message.channel.purge(limit=100)
                                    self.players[x].game_display = await user_channel.send("Waiting for **EVERYONE** to ready up...")
                                else:
                                    await message.channel.purge(limit=1)
                                break


                if len(self.ready_players) == len(self.players) :
                    self.state = 'play'
                    await self.update_screens()

        elif self.state == 'play':
            if message.author.nick == message.channel.name:
                msg = message.content.split(' ')
                if msg[0].lower() in self.dice_commands:
                    await self.dice_commands[msg[0].lower()](message,user_channel)
                else:
                    await message.channel.purge(limit=1)
                count = 0
                winner = None
                for i in self.players:
                    if len(i.dice) != 0:
                        count += 1
                        winner = i
                if count ==1:
                    self.state = 'end'
                    await self.update_statuses_end(winner)

        elif self.state == 'end':
            pass

    async def update_statuses_end(self,winner):
        for p in self.players:
            p.status_message = f'{winner.dude.nick} WINS!'
        await self.update_screens()
    async def   update_screens(self):
        screen = ''
        screen +='-------------------------------------\n'
        screen +='__Players:__\n'
        for x, p in enumerate(self.players):
            for d in p.dice:
                screen += dice_o
            screen += ' ' + p.dude.nick
            if x == self.player_turn_tracker:
                screen += "  <--"
            screen += '\n'
        screen +='-------------------------------------\n'
        screen +='CURRENT BID: '
        if self.recent_bid == None:
            screen += 'nothing has been bid yet'
        else:
            if self.recent_bid[1] == 's':
                img = dice_emotes[0]
            else:
                img = dice_emotes[self.recent_bid[1]]

            screen += f'{self.recent_bid[0]} x {img}'
        screen += '\n'
        screen +='-------------------------------------\n'


        for x, p in enumerate(self.players):
            temp = ''
            if x != self.player_turn_tracker:
                temp += f"It is **{self.players[self.player_turn_tracker].dude.nick}**'s turn\n"
                temp += f"call **bluff**,  call **spot** on, or ask for **help**\n"
            else:
                temp += f"It is **Your** turn\n"
                temp += "You can **bid**, call **bluff**, call **spot** on or ask for **help**\n"
            temp += '-------------------------------------\n'
            try:
                await p.game_display.edit(content=f"{screen + temp}")
            except:
                for chann in self.category.channels:
                    if chann.name == p.dude.nick:
                        break
                p.game_display = await chann.send(screen + temp)

            try:
                await p.status_display.edit(content=p.status_message)
            except:
                for chann in self.category.channels:
                    if chann.name == p.dude.nick:
                        break
                p.status_display = await chann.send(p.status_message)


            dic = ''
            for d in p.dice:
                dic += dice_emotes[d]
            dic += '\n'

            if dic == '\n':
                dic = 'none' + dic
            try:
                await p.dice_display.edit(content=f"{dic}")
            except:
                for chann in self.category.channels:
                    if chann.name == p.dude.nick:
                        break

                p.dice_display = await chann.send(dic)










class Game(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.guild = None
        self.game_type = None
        self.game = None
        self.state = None
        self.players = []
        self.supported_games = ['dice']
        self.bot_category = None
        self.gameimg  ={
            'dice': dice_o
        }
        self.functionDict = {
            None: self.none,
            'start': self.start,
            'play': self.play
        }


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Game Loaded')
    # async def create_lobby(self):

    async def check_ifin_server(self,ctx):
        if ctx.guild == None:
            await ctx.send('Game must be started in a server')
            return False
        elif ctx.guild != self.guild and self.guild is not None:
            await ctx.send(f'Things must happen in: {self.guild}')
            return False

        return True

    @commands.command(name='game')
    async def game(self, ctx, *, command='none'):
        if await self.check_ifin_server(ctx):
            if ctx.message.author.nick == ctx.message.channel.name:
                await ctx.send(f'You are not allowed to type commands in this channel')
            else:
                await self.functionDict[self.state](ctx,command=command)

    @commands.Cog.listener()
    async def on_message(self, message):
        correct_channel_flag = False
        chan = None
        if self.bot_category != None:
            for c in self.bot_category.channels:
                if c.name == message.author.nick:
                    correct_channel_flag = True
                    chan = c
                    break
            if correct_channel_flag:
                # print(message)
                if self.game != None:
                    await self.game.run(message,chan)


    async def play(self, ctx, *, command='none'):
        await ctx.send("you don't need to type !game during actual play")

    async def none(self, ctx, *, command='none'):
        if self.game_type == None:
            if command in self.supported_games :
                if ctx.author.voice == None:
                    await ctx.send(f"You must be connected to a voice channel to start a game")
                    return
                self.game_type = command
                self.guild = ctx.guild
                self.players.append(ctx.author)

                await self.setup_channels(ctx)
                if self.game_type == 'dice':
                    self.game = DiceGame(self.bot_category)
                    print(self.game)

                await ctx.send(f"When everyone is connected to voice channel: {ctx.author.voice.channel} type: '!game start' to begin {self.game_type} {self.gameimg[self.game_type]}")
            else:
                await ctx.send(f"Invalid Game Type: {command}")
                return
        if command in ['start', 'begin']:
            self.state = 'start'
            await self.start(ctx)

    async def destroy_bot_channels(self):
        while(len(self.bot_category.channels)>0):
            try:
                await self.bot_category.channels[0].delete()
            except:
                print(f'deleting of channel failed')
        await self.bot_category.delete()
        self.bot_category = None



    async def start(self,ctx,command='nah'):
        print(f"game state is now {self.state}")

        member_ids = ctx.author.voice.channel.voice_states.keys()
        print(self.guild.channels[0])



        for id in member_ids:
            dude = ctx.guild.get_member(id)
            if not dude.bot:
                if dude not in self.players:
                    self.players.append(dude)

                creat_flag = True

                for d in self.bot_category.channels:
                    if d.name == dude.nick:
                        creat_flag = False
                        break
                if creat_flag:
                    overwrites = {
                        self.guild.default_role: discord.PermissionOverwrite(read_messages=False,send_messages=False),
                        dude: discord.PermissionOverwrite(read_messages=True,send_messages=True )

                        # self.guild.owner: discord.PermissionOverwrite(read_messages=True,send_messages=True)
                    }

                    channel = await self.bot_category.create_text_channel(dude.nick, overwrites=overwrites)
                    attention = ['Listen up','Alright','Hello','HELLOOOO???','Hey','HEY','Yo','Oi!','Take notice','Oye!','Mira!','ねえ!','Привет!','hej!','Heyoo','헤이']
                    await channel.send(f"{rand_obj(attention)} <@!{dude.id}>! Over here you {insult(adjmax=1,article=False)}. \nThis is the channel where you'll be playing! No-one else can interact with or see what's here.\nOnce everyone has typed **READY** the game will begin")
                    # self.bot_category.create_text_channel(dude.nick,)
                    print(f"{dude} added to game")
        self.game.init_players(self.players)
        self.state = 'play'



    async def setup_channels(self,ctx):
        bot_name = 'E-bot'
        if self.bot_category == None:
            for c in self.guild.categories:
                if c.name == bot_name:
                    self.bot_category = c
                    print(f"{bot_name} already exists")
                    await self.destroy_bot_channels()
        if self.bot_category == None:
            self.bot_category = await self.guild.create_category_channel(bot_name)
            print(f"{bot_name} category created")
        print(f"{self.bot_category}")

    # async def destroy_channels(self,ctx):
    #     if self.bot_category != None:
    #         await self.bot_category


def setup(client):
    client.add_cog(Game(client))