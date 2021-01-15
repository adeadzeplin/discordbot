import os


def help(bot, prefix,cmds):
    bot.send_message("Registered commands "+ ", ".join([f"{prefix}{cmd}" for cmd in sorted(cmds.keys())]))

def hello(bot,user,*args):
    bot.send_message(f"Hey {user['name']}! {' '.join(args)} to you too!")








def bbb(bot,user,*args):
    bot.send_message(f"Sending a BBB request {user['name']}!")
    file_name = None
    if len(args) == 1:
        for file in os.listdir('./sounds'):
            if args[0] == file[:-4]:
                file_name = file[:-4]

    data = {
        'user': user,
        'filename':file_name
    }

    bot.PIPES['bbb'].put(data)