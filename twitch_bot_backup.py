import os
from dotenv import load_dotenv
from irc.bot import SingleServerIRCBot
import irc
from requests import get
from lib import cmds

load_dotenv()
ID = os.getenv('twitchclientid')
SECRET = os.getenv('twitchclientsecret')

USERNAME = 'E_botbot'
CHANNEL_NAME = 'adeadzeplin'
OAUTHTOKEN = os.getenv('TWITCHOAUTHTOKEN')



class Bot(SingleServerIRCBot):
    def __init__(self, p):
        # TODO: Move configuration values to a separate config file
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.USERNAME = USERNAME.lower()
        self.CLIENT_ID = ID
        self.TOKEN = OAUTHTOKEN
        self.CHANNEL = f"#{CHANNEL_NAME}"
        self.PIPES = p
        self.s = irc.schedule.DefaultScheduler()
        self.hunt_flag = False
        self.king_flag = False
        self.pachinko_flag = False


        # TODO: Implement error handling for API requests
        url = f"https://api.twitch.tv/kraken/users?login={self.USERNAME}"
        headers = {
            "Client-ID": self.CLIENT_ID,
            "Accept": "application/vnd.twitchtv.v5+json",
        }
        resp = get(url,headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]
        super().__init__([(self.HOST,self.PORT,self.TOKEN)],self.USERNAME,self.USERNAME)
    
    def on_welcome(self,cxn,event): # When bot comes online
        # TODO: Implement error handling for connection failures
        for req in ("membership","tags","commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")
        cxn.join(self.CHANNEL)
        self.send_message("Now online")
        # TODO: Replace print statements with proper logging
        print(f'{USERNAME} is online')
        # TODO: Implement the check_PIPES method and uncomment the following line
        # self.s.add(irc.schedule.PeriodicCommand.after(3, self.check_PIPES()))




    def on_pubmsg(self,cxn,event): # When a chat message happens
        # TODO: Implement rate limiting to prevent spam
        tags = {kvpair["key"]:kvpair["value"] for kvpair in event.tags}
        user = {"name":tags["display-name"],"id":tags["user-id"]}
        message = event.arguments[0]
        if user["name"] != USERNAME:
            cmds.process(self,user,message)

    def on_whisper(self, cxn, event):
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {"name": tags["display-name"], "id": tags["user-id"]}
        message = event.arguments[0]
        if user["name"] != USERNAME:
            cmds.process(self, user, message)
        print('whisper happened')

    def send_message(self,message):
        self.connection.privmsg(self.CHANNEL,message)

    # TODO: Implement error handling for network issues and disconnections
    # TODO: Add methods for handling whispers and other Twitch-specific events
    # TODO: Implement a method to gracefully shut down the bot
    # REVIEW: Consider implementing a more robust command system with decorators
        cmds.process(self, user, message)
        print('whisper happened')

    def send_message(self,message):
        self.connection.privmsg(self.CHANNEL,message)



def run_twitchbot(p):
    bot = Bot(p)
    bot.start()
if __name__ == "__main__":
    run_twitchbot("fuck")