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

        # Initialize game flags
        # REVIEW: Consider using an enum or a more structured approach for game states
        self.hunt_flag = False
        self.king_flag = False
        self.pachinko_flag = False

        # Initialize the Bot with Twitch credentials
        # TODO: Consider moving these credentials to a separate configuration file
        super().__init__(token=f'{ACCESS_TOKEN}', prefix='!', initial_channels=['adeadzeplin'])

    async def event_ready(self):
        # Notify when the bot is ready and logged in
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Simple hello command
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command()
    async def ping(self, ctx: commands.Context):
        # Ping a random chatter
        # TODO: Consider adding error handling for empty chatter list
        randperson = random.randint(0, len(ctx.chatters))
        chatter_list = list(ctx.chatters)
        await ctx.send(f"Hey {chatter_list[randperson].name}! you were randomly pinged by {ctx.author.name}!")

    @commands.command()
    async def bbb(self, ctx: commands.Context):
        # BBB command for sound playback
        # TODO: Implement proper error handling for file not found
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

        # REVIEW: Consider if this pipes mechanism is the best way to handle inter-process communication
        self.PIPES['t2d']['bbb'].put(data)

    async def event_message(self, message):
        # Ignore messages sent by the bot
        if message.echo:
            return

        # Print message content to console
        # TODO: Implement proper logging instead of print statements
        print(message.content)

        # Handle commands in the message
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

# OVERALL NOTES:
# TODO: Implement comprehensive error handling throughout the script
# TODO: Set up a logging system for better debugging and monitoring
# TODO: Move configuration (like credentials and game flags) into a separate config file
# REVIEW: Evaluate the 'pipes' mechanism and consider alternatives if necessary