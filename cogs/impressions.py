import discord
from discord.ext import commands
from insult import insult
import insultdatabase
import enum
import numpy as np
from impression_logic import GameState, joingame,Player



class Impressions(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.state = GameState.Init
        self.cardphrases = []
        self.accentcards = ['British','American','Spanish','Russian'] #,'Robot','Squidward','Pirate','Caveman','FreddieMurcury'
        for i in range(50):
            self.cardphrases.append(insult())
        self.players = []
        self.HANDSIZE = 6
        self.judgeindex = 0
        self.roundaccentcard = []
        self.MINPLAYERS = 2
        self.guild = None
        self.channel = None
        self.host = None
        self.roundcounter = 0
        self.ROUNDLIMIT = 0

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Impression Loaded')

    # def is_guild_owner():
    #     def predicate(ctx):
    #         return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    #     return commands.check(predicate)

    # @commands.check_any(commands.is_owner(),is_guild_owner())
    @commands.command(aliases=['ng','new game','Newgame'],help="Improvised Impressions. Social game meant to be played in VC")
    async def newgame(self, ctx):
        if ctx.guild == None:
            await ctx.send('Game must be started in a server channel')
            return
        else:
            self.guild = ctx.guild
            self.channel = self.client.get_channel(ctx.channel.id)
        if self.state == GameState.Init:
            self.host = ctx.message.author

            self.state = GameState.GetPlayers
            await ctx.send('Waiting for players to join the game')
            print(f"{ctx.message.author} started a new game")
            await self.joingame(ctx)
        else:
            await ctx.send(f'Error: game state is not ready for a new game. State: {self.state}')
            print(f"{ctx.message.author} attempted to start a new game")

    @commands.command(aliases=['JoinGame','jg', 'join', 'Joingame'])
    async def joingame(self, ctx):

        if self.state == GameState.GetPlayers:
            if ctx.guild == self.guild:
                if ctx.channel == self.channel:
                    await ctx.send(joingame(ctx,self.players))
                else:
                    await ctx.send(f'You must join the game in the "{self.channel}" channel')
            else:
                await ctx.send(f'You must join the game in the "{self.guild}" server')
        else:
            response = f'Error: game can not be joined in current state. State: {self.state}'
            print(f"{ctx.message.author} attempted to start a new game")
            await ctx.send(response)

    def fillplayershands(self):
        for player in self.players:
            if player.selection != 'nothing':
                player.hand.pop(int(player.selection))
                player.selection = 'nothing'
            for i in range(self.HANDSIZE):
                if len(player.hand) < self.HANDSIZE:
                    index = np.random.randint(len(self.cardphrases)-1)
                    card = self.cardphrases.pop(index)
                    player.hand.append(card)




    # @commands.check_any(commands.is_owner())
    @commands.command(aliases=['StartGame', 'sg','start game', 'Startgame'])
    async def startgame(self, ctx):
        if self.state == GameState.GetPlayers:
            if ctx.guild == self.guild:
                if ctx.channel == self.channel:
                    if self.host == ctx.message.author:
                        if len(self.players)>= self.MINPLAYERS:
                            self.state = GameState.RoundStart
                            self.ROUNDLIMIT = len(self.players)
                            self.fillplayershands()
                            np.random.shuffle(self.players)
                            cardindex = np.random.randint(len(self.accentcards))
                            self.roundaccentcard = self.accentcards.pop(cardindex)
                            await ctx.send(f'{self.ROUNDLIMIT-self.roundcounter} ROUND(S) REMAINING')
                            await ctx.send(f'{self.players[self.judgeindex].id} Is the impression judge!')
                            await ctx.send(f'\nThe Accent is:\n{self.roundaccentcard} ')
                            print(f"{ctx.message.author} started a new game")
                        else:
                            if len(self.players)==self.MINPLAYERS-1:
                                await ctx.send(f'Not enough players to start the game! {self.MINPLAYERS - len(self.players)} more player needs to join the game')
                            else:
                                await ctx.send(f'Not enough players to start the game! {self.MINPLAYERS-len(self.players)} more players need to join the game')
                            print(f"{ctx.message.author} started a new game")
                    else:
                        await ctx.send(f'Game must be started by the game host: {self.host}')
                        print(f"{ctx.message.author} attempted to start a game in {self.guild}")
                else:
                    await ctx.send(f'Game must be started in the: "{self.channel}" channel')
            else:
                await ctx.send(f'Game must be started in the: "{self.guild}" server')
                print(f"{ctx.message.author} attempted to start a game in {self.guild}")
        else:
            await ctx.send(f'Error: game can not be started in current state. State: {self.state}')
            print(f"{ctx.message.author} attempted to start a game")



    def isleader(self,player_id):
        if player_id == self.players[self.judgeindex].id:
            return True
        else:
            return False

    def get_unready_players(self):
        count = 0
        for p in self.players:
            if p.selection == 'nothing':
                if self.isleader(p.id):
                    pass
                else:
                    count += 1
        return count


    @commands.command(aliases=['view_hand','vh', 'Viewhand'])
    async def viewhand(self, ctx):
        if ctx.guild == None:
            if self.state == GameState.RoundStart or self.state == GameState.RoundPerform:
                for p in self.players:
                    if ctx.message.author == p.id:
                        response =''
                        for i,card in enumerate(p.hand):
                            response += str(i) + ': ' + card +"\n"
                        if p.id == self.players[self.judgeindex].id:
                            if self.get_unready_players() == 1:
                                await ctx.send(f"This round's accent is: {self.roundaccentcard} \nThere is 1 player still picking")
                            else:
                                await ctx.send(f"This round's accent is: {self.roundaccentcard} \nThere are {self.get_unready_players()} players still picking")
                        elif p.selection == 'nothing':
                            await ctx.send(f"This round's accent is: {self.roundaccentcard} \nYou have selected: {p.selection}")
                        else:
                            await ctx.send(f"This round's accent is: {self.roundaccentcard} \nYou have selected: {p.hand[p.selection]}")
                        await ctx.send(response)
                        await ctx.send(f"You have won {len(p.winlist)} rounds")
                        print(f"{ctx.message.author} viewed their hand")
                        break
            else:
                await ctx.send(f'Error: hand can not be viewed in current state. State: {self.state}')
        else:
            await ctx.send(f'{ctx.message.author} you must view your hand privately. DM me, the bot, private commands.')



    @commands.command(aliases=['pickcard', 'select','sc', 'pc'])
    async def selectcard(self, ctx,selection):
        if ctx.guild == None:
            if self.state == GameState.RoundStart:
                for p in self.players:
                    if ctx.message.author == p.id:
                        if self.isleader(p.id):
                            await ctx.send(f"You may not select anything while judging")
                            print(f"{ctx.message.author} attempted to select a card while leading")
                        else:
                            if int(selection) >= 0 and int(selection) < len(p.hand):
                                p.selection = int(selection)
                                await ctx.send(f"You selected: {p.hand[p.selection]}")
                                print(f"{ctx.message.author} selected a card")

                                if self.get_unready_players() == 0:
                                    self.state = GameState.RoundPerform

                                    await self.channel.send(f"Everyone has selected their card to play.")
                                    await self.channel.send(f"People may now take turns doing impressions")
                                    # await self.channel.send(f"The round judge may enter '!judge' to end the round")
                                    await self.channel.send(f"Players may enter '!show' to display their card")
                                    await self.channel.send(f"Judge may enter '!show' to display remaining players")
                                    await self.channel.send(f"Judge will select a winner when everyone has shown their card")
                            else:
                                await ctx.send(f"Incorrect selection")
                                print(f"{ctx.message.author} tried to select card: {selection} and failed")
            else:
                await ctx.send(f'Error: Card cannot be selected in current state. State: {self.state}')
        else:
            await ctx.send(f'{ctx.message.author} you must select your card privately. DM me, the bot, private commands.')

    @commands.command(aliases=['show', 'Show_card'])
    async def showcard(self,ctx):
        endroundFlag = True
        if self.state == GameState.RoundPerform:
            if ctx.guild == self.guild:
                if ctx.channel == self.channel:
                    for p in self.players:
                        if ctx.message.author == p.id:
                            if self.isleader(p.id):
                                response = f'The Accent for this round is: {self.roundaccentcard}\n'
                                for p in self.players:
                                    if p.shownflag == False:
                                        if self.isleader(p.id):
                                            pass
                                        else:
                                            response += str(p.id) + ' has not shown their card yet\n'
                                # await self.channel.send(response)

                            else:
                                response = f"{ctx.message.author}'s card:\n{p.hand[p.selection]}\n\n"
                                p.shownflag = True
                            await self.channel.send(response)
                            break

                    for p in self.players:
                        if self.isleader(p.id):
                            pass
                        else:
                            if p.shownflag == False:
                                endroundFlag = False
                                break

                    if endroundFlag:
                        await self.channel.send("Everyone has shown their card. Judge will now select a winner")
                        self.state = GameState.RoundJudge
                        cardlist = ''
                        for i, p in enumerate(self.players):
                            if self.isleader(p.id):
                                cardlist += f"{i}: {p.id} - Round Judge \n"
                                pass
                            else:
                                cardlist += f"{i}: {p.id} - {p.hand[p.selection]} \n"
                        await self.channel.send(cardlist)
                    else:
                        pass
                        # await self.channel.send(response)
                else:
                    await ctx.send(f'You must show your card to the Channel: {self.channel} ')
            else:
                await ctx.send(f'You must show your card to\n the Server: {self.guild}\n the Channel: {self.channel} ')
        else:
            await ctx.send(f'Error: Card cannot be shown in current state. State: {self.state}')


    # @commands.command(aliases=['j'])
    # async def judge(self,ctx):
    #     response =''
    #     if self.state == GameState.RoundPerform:
    #         if self.isleader(ctx.message.author):
    #             endroundFlag = True
    #             for p in self.players:
    #
    #                 if p.shownflag == False:
    #                     if self.isleader(p.id):
    #                         pass
    #                     else:
    #                         endroundFlag = False
    #                         response += str(p.id) + ' has not shown their card yet\n'
    #             if endroundFlag:
    #                 await self.channel.send("Everyone has shown their card. Judge will now select a winner")
    #                 self.state = GameState.RoundJudge
    #                 cardlist = ''
    #                 for i, p in enumerate(self.players):
    #                     if self.isleader(p.id):
    #                         cardlist += f"{i}: {p.id} - Round Judge \n"
    #                         pass
    #                     else:
    #                         cardlist += f"{i}: {p.id} - {p.hand[p.selection]} \n"
    #                 await self.channel.send(cardlist)
    #             else:
    #                 await ctx.send(response)
    #     else:
    #         await ctx.send(f'Error: judgment cannot begin in current state. State: {self.state}')


    async def startnewround(self,ctx):
        self.state = GameState.RoundStart
        for p in self.players:
            if p.selection != 'nothing':
                p.hand.pop(int(p.selection))
        self.fillplayershands()
        cardindex = np.random.randint(len(self.accentcards))
        self.roundaccentcard = self.accentcards.pop(cardindex)
        await ctx.send(f'{self.ROUNDLIMIT - self.roundcounter} REMAINING ROUND(S)')
        await ctx.send(f'{self.players[self.judgeindex].id} Is the impression judge!')
        await ctx.send(f'\nThe Accent is:\n{self.roundaccentcard} ')


    def gamewinner(self):
        maxscore = 0
        maxid = 0
        for p in self.players:
            if len(p.winlist)>maxscore:
                maxscore = len(p.winlist)
                maxid = p
        return maxid




    async def gameover(self,ctx):
        if self.state == GameState.GameOver:

            extension = 'impressions'
            winner = self.gamewinner()
            await self.channel.send(f"\n\n\n{winner.id} has won the game with {len(winner.winlist)} card(s)!")


    async def resetround(self,ctx):
        self.judgeindex += 1
        if self.judgeindex >= len(self.players):
            self.judgeindex = 0

        self.roundcounter += 1
        if self.roundcounter < self.ROUNDLIMIT:
            self.state = GameState.RoundStart
            await self.startnewround(ctx)
        else:
            self.state = GameState.GameOver
            await self.gameover(ctx)





    @commands.command(aliases=['selectwinner','choosewinner','cw','sw','pw'])
    async def pickwinner(self,ctx,winnerchoice):
        winchoi = int(winnerchoice)
        if self.state == GameState.RoundJudge:
            if self.isleader(ctx.message.author):
                if self.players[winchoi] == self.players[self.judgeindex]:
                    await self.channel.send("The round Judge "+ str(ctx.message.author) + " is "+ insult()+". They tried to pick themselves as the winner" )
                    await self.channel.send(f"{ctx.message.author} still needs to pick a winner")
                else:
                    response = f"{self.players[winchoi].id} won the round by doing an accent: {self.roundaccentcard}\n Saying: "
                    response +=  f"{self.players[winchoi].hand[self.players[winchoi].selection]}"
                    await self.channel.send(response)
                    print(f"{self.players[winchoi].id} won the round")
                    self.players[winchoi].winlist.append(self.roundaccentcard)
                    self.roundaccentcard =[]
                    await self.resetround(ctx)

            else:
                await ctx.send(f'Only the round judge can pick a winner. Round leader is: {self.players[self.judgeindex].id}')

        else:
            await ctx.send(f'Error: Winner cannot be chosen in current state. State: {self.state}')


def setup(client):
    client.add_cog(Impressions(client))