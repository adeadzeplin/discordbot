import discord
from discord.ext import commands
import discord.client
import asyncio
import palacelogic as p
import enum
import random
class GameState(enum.Enum):
    pendstart = 1
    init = 2
    cancel = 3
    setup = 4
    play = 5
class Suit(enum.Enum):
    spade = 's'
    heart = 'h'
    club = 'c'
    diamond = 'd'
class Num(enum.Enum):
    nA = 14
    n2 = 15
    n3 = 3
    n4 = 4
    n5 = 16
    n6 = 6
    n7 = 7
    n8 = 8
    n9 = 9
    n10= 17
    nJ = 11
    nQ = 12
    nK = 13
class Card():
    def __init__(self,label,suit):
        self.label = label
        self.suit = suit
    def __lt__(self,other):
        if (self.label.value < other.label.value):
            return True
        else:
            return False

class Player():
    def __init__(self, id , name):
        self.id = id
        self.name = name
        self.hand =[]
        self.palacetop = []
        self.palacehidden = []
        self.selection = []
        self.display_message = None

    def player_depug_print(self):
        fstring = ''
        fstring += f'Id:{self.id}\n'
        fstring += f'Hand: '
        for c in self.hand:
            fstring += f' {c.label.name}{c.suit.name}'
        fstring += f'\nPalace Top: '
        for c in self.palacetop:
            fstring += f' {c.label.name}{c.suit.name}'
        fstring += f'\nPalace Hidden: '
        for c in self.palacehidden:
            fstring += f' {c.label.name}{c.suit.name}'
        fstring += f'\nSelected Cards: '
        for c in self.selection:
            fstring += f' {c.label.name}{c.suit.name}'

        return fstring

class Game_palace():
    def __init__(self,player1,p1name,player2,p2name):
        self.player1 = Player(player1,p1name)
        self.player2 = Player(player2,p2name)
        self.state = GameState.pendstart
        self.turn = random.randint(0,1)
        self.deck = self.new52deck()
        self.pile = []
        self.PALACESIZE = 3
        self.CARDBACK = '<:cardbackgrn:747592966704463965>'
        self.AWAYHANDMAX = 6
        self.MINCARDSINHAND = 3

    def game_debug_print(self):
        outstring = f''
        outstring += f'Game state: {self.state}\n'
        outstring += f"Player {self.turn + 1}'s Turn\n"
        outstring += f'There are {len(self.deck)} cards in the deck\n'
        outstring += f'Player 1: {self.player1.player_depug_print()}\n'
        outstring += f'_____________________________________________\n'
        outstring += f'Player 2: {self.player1.player_depug_print()}\n'
        return outstring
    def awayhandstring(self,player):
        out = ''
        for i in range(len(player.hand)):
            if i < self.AWAYHANDMAX:
                out += f'{self.CARDBACK} '
            else:
                out += f' +{len(player.hand) - self.AWAYHANDMAX} '
                break
        return out
    def homehandstring(self,player):
        out = ''
        for c in player.hand:
            out += f':{c.label.name}{c.suit.value}:'
        return out
    def palacestring(self,player):
        out = ''
        for i in range(self.PALACESIZE):
            if i < len(player.palacetop):
                for j,c in enumerate(player.palacetop):
                    if j == i:
                        out += f':{c.label.name}{c.suit.value}:'
                        break
            else:
                for j in range(self.PALACESIZE):
                    if j == i:
                        out += f'{self.CARDBACK}'
                        break
        return out
    def playerdisplay(self, playerselect):

        if playerselect == 1:
            playerhome = self.player1
            playeraway = self.player2
        elif playerselect == 2:
            playerhome = self.player2
            playeraway = self.player1
        else:
            return "FUCK PLAYER DISPLAY BROKE"
        output = ''
        apalace = self.palacestring(playeraway)
        ahand   = self.awayhandstring(playeraway)
        ahandlen = len(playeraway.hand)

        decklen = len(self.deck)
        pilelen = len(self.pile)

        hpalace = self.palacestring(playerhome)
        hhand   = self.homehandstring(playerhome)
        hhandlen = len(playerhome.hand)

        if self.turn+1 == playerselect:
            turn = 'your'
        else:
            turn = "opponent's"



        output += f"-----------------------------------\n"
        output +=f"| {playeraway.name}'s hand:               \n"
        output +=f"| {apalace}                              \n"
        output +=f"| {ahand}                                 \n"
        output +=f"|                                        \n"
        output +=f"| Pile ({pilelen}): Last played           \n"
        output +=f"| Deck {decklen}                     \n"
        output +=f"|                                        \n"
        output +=f"| {hpalace}                   \n"
        output +=f"| {hhand}         \n"
        output +=f"------------------------------------\n"
        # output +=f"                                        \n"
        output +=f"Select Cards by typing the symbols.     \n"
        output +=f"It's {turn} turn                        \n"

        # output += f"```\n"

        return output

    def new52deck(self):
        temp = []
        for n in Num:
            for s in Suit:
                temp.append(Card(n,s))
        random.shuffle(temp)
        return temp.copy()

    def init(self, pla, msg):
        if pla == 2:
            if msg.content.lower() in ['yes', 'y']:
                self.state = GameState.init
            elif msg.content.lower() in ['no', 'n']:
                self.state = GameState.cancel

    def startg(self):
        for i in range(0,3):
            self.player1.palacehidden.append(self.deck.pop())
            self.player2.palacehidden.append(self.deck.pop())
        for i in range(0, 6):
            self.player1.hand.append(self.deck.pop())
            self.player2.hand.append(self.deck.pop())
        self.player1.hand.sort()
        self.player2.hand.sort()
        self.state = GameState.setup


class Palace(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.games = []
        self.players = []

    def getgame(self,id):
        for i,g in enumerate(self.games):
            if id == g.player1.id:
                return i, 1
            elif id == g.player2.id:
                return i,2
        return None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Palace Loaded')

    @commands.command(name='debug', help='debug command', aliases=['d'])
    async def debug(self, ctx, *, Target="ctx.message.author"):
        gameindex = self.getgame(ctx.author.id)
        if gameindex == None:
            print('Player not in game')
        else:

            tempgame = self.games[gameindex[0]]
            print('____________')
            print(tempgame.game_debug_print())
            print('____________')


    @commands.Cog.listener()
    async def on_message(self,message):
        if message.content.startswith('!'):
            pass
        elif message.author.id in self.players:
            gameindex, player = self.getgame(message.author.id)
            [print(i) for i in self.players]
            if gameindex == None:
                [print(i) for i in self.players]
                print('PLAYER IN PLAYERLIST BUT NOT IN A GAME')
            else:
                if message.content == 'quit':
                    self.games[gameindex].state = GameState.cancel
                if self.games[gameindex].state == GameState.pendstart:
                    self.games[gameindex].init(player,message)
                if self.games[gameindex].state == GameState.init:
                    msg = f"Game Accepted! Please stand by.."
                    self.games[gameindex].player1.display_message = await self.setplayermsg(self.games[gameindex].player1.id,msg)
                    self.games[gameindex].player2.display_message = await self.setplayermsg(self.games[gameindex].player2.id, msg)
                    self.games[gameindex].startg()
                if self.games[gameindex].state == GameState.setup:

                    await self.games[gameindex].player1.display_message.edit(content=f"{self.getdisplay(gameindex,1)}")
                    await self.games[gameindex].player2.display_message.edit(content=f"{self.getdisplay(gameindex,2)}")

                    # self.games[gameindex].player1.display_message =  await self.msgplayer(self.games[gameindex].player1.id,msg)

                if self.games[gameindex].state == GameState.cancel:
                    self.removeplayer(self.games[gameindex].player1.id)
                    self.removeplayer(self.games[gameindex].player2.id)
                    self.games.pop(gameindex)
    def getdisplay(self,index,player):
        display = self.games[index].playerdisplay(player)
        return display
    def removeplayer(self,id):
        for x, i in enumerate(self.players):
            if i == id:
                self.players.pop(x)
                print('player removed')
    async def setplayermsg(self,id,msg):
        user = self.client.get_user(id)
        return await user.send(f'{msg}')

    async def msgplayer(self, id,msg):
        user = self.client.get_user(id)
        await user.send(f'{msg}')

    @commands.command(name='palace',help=': chalange someone to a game of palace',aliases=['p'])
    async def palace(self,ctx,*,Target="ctx.message.author"):
        await ctx.channel.purge(limit=1)
        temp = int(Target.strip('<!@>'))
        if ctx.message.author in self.players or temp in self.players:
            if ctx.message.author in self.players:
                await ctx.send("You are already in a game and cannot begin another one")
            else:
                await ctx.send(f"{Target} is already in a game and cannot begin another one")
        else:

            user = self.client.get_user(temp)
            print(user)
            await user.send(f'{ctx.message.author} Has Challenged you to a game of Palace.\nDo you Accept? yes or no')
            # await self.client.bot.send_message(Target, 'boop')
            self.players.append(ctx.message.author.id)
            self.players.append(temp)

            hostuser = self.client.get_user(ctx.message.author.id)
            awayuser =self.client.get_user(temp)
            self.games.append(Game_palace(ctx.message.author.id,hostuser,temp,awayuser))





def setup(client):
    client.add_cog(Palace(client))