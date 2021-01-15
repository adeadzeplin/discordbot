import multiprocessing

from discord_bot import run_discordbot
from twitch_bot import run_twitchbot

def main():

    pipes = {
        'bbb': multiprocessing.Queue(),

    }



    discord_bot = multiprocessing.Process(target=run_discordbot,args=(pipes,))
    twitch_bot = multiprocessing.Process(target=run_twitchbot,args=(pipes,))
    discord_bot.start()
    twitch_bot.start()
    # wait until process 1 is finished
    discord_bot.join()
    twitch_bot.join()


if __name__ == "__main__":
    main()