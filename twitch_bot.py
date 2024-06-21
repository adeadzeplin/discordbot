import os
from dotenv import load_dotenv
from twitchio.ext import commands
from lib import cmds
from requests import get

import random

load_dotenv()
ID = os.getenv('twitchclientid')
SECRET = os.getenv('twitchclientsecret')

USERNAME = 'E_botbot'
CHANNEL_NAME = 'adeadzeplin'
OAUTHTOKEN = os.getenv('TWITCHOAUTHTOKEN')


ACCESS_TOKEN = os.getenv('TWITCHIO_ACCESS_TOKEN')

class Bot(commands.Bot):
    def __init__(self, p):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.USERNAME = USERNAME.lower()
        self.CLIENT_ID = ID
        self.TOKEN = OAUTHTOKEN
        self.CHANNEL = f"#{CHANNEL_NAME}"
        self.PIPES = p

        self.hunt_flag = False
        self.king_flag = False
        self.pachinko_flag = False

        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=f'{ACCESS_TOKEN}', prefix='!', initial_channels=['adeadzeplin'])

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command()
    async def ping(self, ctx: commands.Context):
        randperson = random.randint(0,len(ctx.chatters))
        chatter_list = list(ctx.chatters)
        await ctx.send(f"Hey {chatter_list[randperson].name }! you were randomly pinged by {ctx.author.name}!")


    @commands.command()
    async def bbb(self, ctx: commands.Context):
        await ctx.send(f"Sending a BBB request {ctx.author.name}!")
        file_name = None
        msg = ctx.message.content
        args = msg.split(" ")
        if len(args) == 2:
            for file in os.listdir('./sounds'):
                if args[1] == file[:-4]:
                    file_name = file[:-4]
                    print(file_name, file[:-4])
        data = {
            'user': ctx.author.name,
            'filename': file_name
        }

        self.PIPES['t2d']['bbb'].put(data)

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)



    @commands.command()
    async def king(self, ctx: commands.Context):

        args = ctx.message.content.split(" ")
        args.pop(0)#get rid of command from ags

        if self.king_flag == False and ctx.author.name == 'adeadzeplin':
            await ctx.send(f"Sending a game init request {ctx.author.name}!")
            self.hunt_flag = False
            self.king_flag = True
            self.pachinko_flag = False

        elif len(args)>0:
            if len(args) == 2:
                data = {
                    'user': ctx.author.name,
                    'args': args
                }
                self.PIPES['t2s']['data'].put(data)
            elif args[0].lower() == 'join':

                temp = await ctx.author.user()

                await ctx.send(f"{ctx.author.name} Joined king of the hill")
                data = {
                    'user': ctx.author.name,
                    'args': args,
                    'logo': temp.profile_image
                }
                self.PIPES['t2s']['data'].put(data)

            elif (ctx.author.name == 'adeadzeplin'):
                data = {
                    'user': ctx.author.name,
                    'args': args
                }
                self.PIPES['t2s']['data'].put(data)


def run_twitchbot(p):
    bot = Bot(p)
    bot.run()
if __name__ == "__main__":
    run_twitchbot("fuck")