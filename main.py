import multiprocessing
import asyncio

from discord_bot import run_discordbot
from twitch_bot import run_twitchbot
from data_emit_server import data_server

def main():
    # Initialize inter-process communication pipes
    # REVIEW: Consider using a more structured approach for IPC, like message queues or RPC
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

    # Initialize Twitch bot process
    # TODO: Implement error handling for process creation and management
    twitch_bot = multiprocessing.Process(target=run_twitchbot, args=(pipes,))
    #twitch_bot.start()  # TODO: Uncomment this line when Twitch bot is ready to be used

    # Initialize Discord bot process
    discord_bot = multiprocessing.Process(target=run_discordbot, args=(pipes,))
    discord_bot.start()
    
    # Run data_server in the main process
    # REVIEW: Consider running this in a separate process for better isolation
    asyncio.run(data_server(pipes))

    # Wait for bot processes to finish
    # TODO: Implement proper shutdown mechanism for graceful termination
    discord_bot.join()
    twitch_bot.join()

if __name__ == "__main__":
    main()

# OVERALL NOTES:
# TODO: Implement logging for better debugging and monitoring
# TODO: Add error handling and recovery mechanisms for process failures
# REVIEW: Consider using a configuration file for process settings and pipe structure