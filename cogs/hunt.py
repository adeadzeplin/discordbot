import discord
from discord.ext import commands
import numpy as np
import ffmpeg
import asyncio
import time
# import  sounddevice as sd
from insult import insult
import insultdatabase
import time
import numpy as np

import hunt_logic as hl


class Player():
    def __init__(self,player_id,msg):
        self.id = player_id
        self.msg = msg
        self.game = hl.Basilesc()
        self.state  ='init'
        self.lastcalled = time.perf_counter()


class Hunt(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.players = []
        self.player_ids = []



    def getindexid(self,id):
        for index, p in enumerate(self.player_ids):
            if p == id:
                return index
    def getplayer(self, ID):
        return self.player_ids[self.getindexid(ID)]

    async def load_animation(self,index,message):
        await self.players[index].msg.edit(content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING...... \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING|..... \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING||.... \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING||||.. \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING|||||. \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING|||||| \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING||||||D \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(
            content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING||||||DO \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(
            content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING||||||DON \n```")
        await asyncio.sleep(.9)
        await self.players[index].msg.edit(
            content=f"```\nYou have selected: '{message.content}'\nControls:  WASD to move    0 to use item\nLOADING||||||DONE\n```")
        await asyncio.sleep(.9)
        messg, ddd = self.players[index].game.getscreenstring()
        await self.players[index].msg.edit(content=f"{messg}")


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Hunt Loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author in self.player_ids:
            index = self.getindexid(message.author)
            if message.content == 'reset':
                self.players.pop(index)
                self.player_ids.pop(index)
                return
            if time.perf_counter() - self.players[index].lastcalled > 60*5 : #player timeout
                await self.players[index].msg.edit(content=f"```\n{self.player_ids[index]} has been timed out: \n```")
                await message.channel.purge(limit=1)

                self.players.pop(index)
                self.player_ids.pop(index)
                return
            else:
                self.players[index].lastcalled = time.perf_counter()


            if self.players[index].state == 'init':
                if len(message.content) == 1:
                    self.players[index].game.player.icon = f'{message.content} '
                    self.players[index].game.screen[self.players[index].game.player.y][self.players[index].game.player.x] = self.players[index].game.player.icon
                    await message.channel.purge(limit=1)

                    await self.load_animation(index,message)
                    self.players[index].state = 'run'

                else:
                    await self.players[index].msg.edit(content=f"```\nYou MUST select a single character. Such as '+'\n'{message.content}' is not allowed\n```")
                    await asyncio.sleep(.9)
                    await message.channel.purge(limit=1)
            elif self.players[index].state == 'run':
                self.players[index].game.updategame(message.content)
                await message.channel.purge(limit=1)
                mesg, status = self.players[index].game.getscreenstring()
                self.players[index].state = status
                await self.players[index].msg.edit(content=f"{mesg}")
                await asyncio.sleep(1)
            elif self.players[index].state == 'lose':
                await self.players[index].msg.edit(content=f"{message.author} I'm sure you tried your best <:kekw:722948944019325091> <:kekw:722948944019325091>")
                self.players.pop(index)
                self.player_ids.pop(index)
                await asyncio.sleep(.9)

            elif self.players[index].state == 'win':
                await self.players[index].msg.edit(content=f"<:pogchamp:682006550122201128> <:pogchamp:682006550122201128> {message.author} Beat BasliEsc! <:pogchamp:682006550122201128> <:pogchamp:682006550122201128>")
                self.players.pop(index)
                self.player_ids.pop(index)
                await asyncio.sleep(.9)

    # @commands.command(aliases=['t'])
    # async def tryer(self, ctx, *, InsultTarget="ctx.message.author"):
        # message = await ctx.send(content=f" ")
        # self.getblankscreen()

    @commands.command(aliases = ['bas'] )
    async def basilisk(self, ctx, *, InsultTarget="ctx.message.author"):
        print(f"{ctx.message.author} called the h command in '{ctx.guild}' in channel: {ctx.channel}")

        if ctx.message.author not in self.player_ids:
            await ctx.channel.purge(limit=1)

            self.player_ids.append(ctx.message.author)
            message = await ctx.send(content=f"```\nEnter a symbol for your character\n```")
            await asyncio.sleep(.9)
            temp = Player(ctx.message.author, message)
            self.players.append(temp)

            # await ctx.send(content=f"Init Complete")
            # await asyncio.sleep(2)

        # else:
        #     index = self.getindexid(ctx.message.author)
        #     self.players[index].c += 1
        #
        #     ballname = ':large_blue_diamond: '
        #     emp = '<:empty:737044654414889031>'
        #     ball = ':large_blue_diamond: '
        #
        #     frames = 40
        #     for f in range(frames):
        #         ballprevy = self.players[index].ball.y
        #
        #         self.players[index].ball.x += self.players[index].ball.xvec
        #         self.players[index].ball.y += self.players[index].ball.yvec
        #
        #         if self.players[index].ball.x >=self.xbounds:
        #             self.players[index].ball.x = self.xbounds-1
        #             self.players[index].ball.xvec *= -1
        #         elif self.players[index].ball.x < 0:
        #             self.players[index].ball.x = 0
        #             self.players[index].ball.xvec *= -1
        #
        #         if self.players[index].ball.y >=self.ybounds:
        #             self.players[index].ball.y = self.ybounds-1
        #             self.players[index].ball.yvec *= -1
        #         elif self.players[index].ball.y < 0:
        #             self.players[index].ball.y = 0
        #             self.players[index].ball.yvec *= -1
        #
        #         if int(self.players[index].ball.y) == int(ballprevy):
        #             row = ''
        #             for x in range(self.xbounds):
        #                 if x == int(self.players[index].ball.x):
        #                     row += ballname
        #                 else:
        #                     row += emp
        #
        #             await self.players[index].screen[int(self.players[index].ball.y)].edit(content=f"{row}")
        #             await asyncio.sleep(.9)
        #         else:
        #             newrow = ''
        #             oldrow = ''
        #             for x in range(self.xbounds):
        #                     oldrow += emp
        #
        #
        #             for x in range(self.xbounds):
        #                 if x == int(self.players[index].ball.x):
        #                     newrow += ballname
        #                 else:
        #                     newrow += emp
        #
        #             await self.players[index].screen[int(self.players[index].ball.y)].edit(content=f"{newrow}")
        #             await asyncio.sleep(.9)
        #             await self.players[index].screen[int(ballprevy)].edit(content=f"{oldrow}")
        #             await asyncio.sleep(.9)

                # await asyncio.sleep(.9)
            # await ctx.send(content=f"Complete")


            # delaylist = []

            # sec = time.perf_counter()
            # maths = int((sec - intialcall)*1000)
            # delaylist.append(maths)

            # print(f"{maths, i}:{np.mean(delaylist)}:{np.std(delaylist)}")
            # intialcall = sec
            # await self.players[index].message.edit(content=f"{self.players[index].id} called the !h command: {self.players[index].c} time(s)")
            # await asyncio.sleep(.9)


        # @client.command()
        # async def test(ctx):
        #     message = await ctx.send("hello")
        #     await asyncio.sleep(1)
        #     await message.edit(content="newcontent")

        

        # async def insultuser(self, ctx, *, InsultTarget="ctx.message.author"):
        #     if InsultTarget == "ctx.message.author":
        #         InsultTarget = ctx.message.author
        #     if InsultTarget == '<@!725508807077396581>' or InsultTarget == 'E-bot':
        #         response = f"{ctx.message.author} Insult me yourself you dumb fucking coward"
        #     else:
        #         response = str(InsultTarget) + " is " + insult()
        #     print(f"{ctx.message.author} insulted {InsultTarget}")
        #
        #     await ctx.send(response)




        # await ctx.channel.purge(limit=1)
        # server = ctx.message.guild
        # voicechannels = []
        # for chan in server.channels:
        #     if isinstance(chan,discord.VoiceChannel):
        #         voicechannels.append(chan)
        # number_of_bs = number_of_b
        # print(number_of_bs)
        # # if number_of_bs >= 6:
        # #     await ctx.send(f'{ctx.message.author} tried to be cancerous by trying to have the bot say {number_of_bs}')
        # #     number_of_bs = 5
        #
        # for i in range(number_of_bs):
        #     # await asyncio.sleep(np.random.randint(60*10))
        #     randindex = np.random.randint(len(voicechannels))
        #
        #     randchannel = voicechannels[randindex]
        #     await asyncio.sleep(np.random.randint(3)) # np.random.randint(60*2)
        #     vc = await randchannel.connect(timeout=60.0,reconnect=True)
        #     await asyncio.sleep(np.random.randint(1,8))
        #
        #     vids = self.load_soundfiles()
        #     print(len(vids))
        #     randvid = np.random.randint(len(vids))
        #     vc.play(discord.FFmpegPCMAudio(vids[randvid],executable='C:/ffmpeg/bin/ffmpeg'))
        #     while vc.is_playing():
        #         await asyncio.sleep(.1)
        #
        #     await vc.disconnect(force=True)
        #     print(f"bbbbing in {ctx.message.guild} sound file {vids[randvid]}")



        # for i,cli in enumerate(self.client.voice_clients):
        #     await self.client.voice_clients[i].disconnect()
        # print(f"{ctx.message.author} called the b command in {ctx.message.guild} and it ran {number_of_bs} times")
def setup(client):
    client.add_cog(Hunt(client))