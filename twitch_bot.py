import os
from dotenv import load_dotenv
from irc.bot import SingleServerIRCBot
from requests import get
from lib import cmds

load_dotenv()
ID = os.getenv('twitchclientid')
SECRET = os.getenv('twitchclientsecret')

USERNAME = 'E_botbot'
CHANNEL_NAME = 'adeadzeplin'
OAUTHTOKEN = os.getenv('TWITCHOAUTHTOKEN')


class Bot(SingleServerIRCBot):
    def __init__(self, q):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.USERNAME = USERNAME.lower()
        self.CLIENT_ID = ID
        self.TOKEN = OAUTHTOKEN
        self.CHANNEL = f"#{CHANNEL_NAME}"
        self.QUE = q

        url = f"https://api.twitch.tv/kraken/users?login={self.USERNAME}"
        headers = {
            "Client-ID": self.CLIENT_ID,
            "Accept": "application/vnd.twitchtv.v5+json",
        }
        resp = get(url,headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]
        super().__init__([(self.HOST,self.PORT,self.TOKEN)],self.USERNAME,self.USERNAME)

    def on_welcome(self,cxn,event): # When bot comes online
        for req in ("membership","tags","commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")
        cxn.join(self.CHANNEL)
        self.send_message("Now online")
        print(f'{USERNAME} is online')

    def on_pubmsg(self,cxn,event): # When a chat message happens
        tags = {kvpair["key"]:kvpair["value"] for kvpair in event.tags}
        user = {"name":tags["display-name"],"id":tags["user-id"]}
        message = event.arguments[0]
        if user["name"] != USERNAME:
            cmds.process(self,user,message)

    def send_message(self,message):
        self.connection.privmsg(self.CHANNEL,message)

def run_twitchbot(q):
    bot = Bot(q)
    bot.start()
if __name__ == "__main__":
    run_twitchbot("fuck")