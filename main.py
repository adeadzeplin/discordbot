import multiprocessing

from discord_bot import run_discordbot
from twitch_bot import run_twitchbot
from data_emit_server import data_server




def main():

    pipes = {
        't2d': {
            'bbb': multiprocessing.Queue(),
            'hunt': multiprocessing.Queue(),

        },
        't2s': {
            'data': multiprocessing.Queue()
        },
        's2d': {
            'bbb': multiprocessing.Queue()
        },
    }


    twitch_bot = multiprocessing.Process(target=run_twitchbot,args=(pipes,))
    #twitch_bot.start()
    discord_bot = multiprocessing.Process(target=run_discordbot,args=(pipes,))
    discord_bot.start()
    data_service = multiprocessing.Process(target=data_server, args=(pipes,))
    #data_service.start()




    # wait until process 1 is finished
    discord_bot.join()
    twitch_bot.join()
    data_service.join()

if __name__ == "__main__":
    main()
    # run_twitchbot(None)