import enum
import numpy as np

class GameState(enum.Enum):
    Init = 0
    GetPlayers = 1
    RoundStart = 2
    RoundPerform = 3
    RoundJudge = 4
    GameOver = 5

class Player():
    def __init__(self, id):
        self.id = id
        self.hand = []
        self.winlist = []
        self.selection = 'nothing'
        self.shownflag = False

def joingame(ctx,players):

    joiningFlag = True
    for p in players:
        if p.id == ctx.message.author:
            joiningFlag = False
            response = f"@{ctx.message.author}: You're already in the game"
            print(f"@{ctx.message.author}: is already in the game")
    if joiningFlag:
        players.append(Player(ctx.message.author))
        if len(players) == 1:
            response = f"@{ctx.message.author}: Joined the game.\n{len(players)} player ready to play"
        else:
            response = f"@{ctx.message.author}: Joined the game.\n{len(players)} players ready to play"
        print(f"@{ctx.message.author}: Joined in the game. {len(players)} ready to play")
    return response

# def startgame()