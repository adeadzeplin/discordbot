from time import time
from . import misc

# TODO: Consider moving PREFIX to a configuration file
PREFIX = "!"

cmds = {
    "hello": misc.hello,
    "bbb": misc.bbb,
    "basilisk": misc.basilisk,
    "king": misc.king,
    "info":misc.info,
    "pachinko":misc.pachinko
}


def process(bot, user, message):
    # TODO: Implement error handling for malformed commands
    if message.startswith(PREFIX):
        cmd = message.split(" ")[0][len(PREFIX):]
        args = message.split(" ")[1:]
        perform(bot,user,cmd,*args)
    elif bot.hunt_flag == True:
        args = message.split(" ")
        perform(bot, user, 'basilisk', *args)
    elif bot.pachinko_flag == True:
        args = message.split(" ")
        perform(bot, user, 'pachinko', *args)
    elif bot.king_flag == True:
        if user['name'] == 'adeadzeplin':
            multi = message.split(' | ')
            for m in multi:
                args = m.split(" ")
                perform(bot, user, 'king', *args)
        else:
            args = message.split(" ")
            perform(bot, user, 'king', *args)

def perform(bot,user,cmd,*args):
    # TODO: Implement rate limiting for command execution
    for name, func in cmds.items():
        if cmd == name:
            func(bot,user,*args)
            # TODO: Replace print statements with proper logging
            print(f"{user['name']} called the command: {PREFIX}{name} {args}")
            return
    if cmd == "help":
        misc.help(bot,PREFIX,cmds)
    else:
        bot.send_message(f"{user['name']}, \"{cmd}\" isn't a registered command.")

# TODO: Implement a system for dynamically loading and unloading commands
# TODO: Add error handling for command execution failures
# REVIEW: Consider implementing a permission system for commands
# TODO: Implement command aliases to allow multiple names for the same command