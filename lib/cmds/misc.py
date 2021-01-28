import os
from requests import get



def help(bot, prefix,cmds):
    bot.send_message("Registered commands "+ ", ".join([f"{prefix}{cmd}" for cmd in sorted(cmds.keys())]))

def hello(bot,user,*args):
    bot.send_message(f"Hey {user['name']}! {' '.join(args)} to you too!")

def king(bot,user,*args):
    if bot.king_flag == False and user['name'] == 'adeadzeplin':
        bot.send_message(f"Sending a game init request {user['name']}!")
        bot.hunt_flag = False
        bot.king_flag = True
    elif len(args) == 2:
        data = {
            'user': user,
            'args':args
        }
        bot.PIPES['t2s']['data'].put(data)
    # elif (user['name'] == 'adeadzeplin'):
    #
    #     data = {
    #         'user': user,
    #         'args': args
    #     }
    #     bot.PIPES['t2s']['data'].put(data)

    elif args[0] == 'join':
        url = f"https://api.twitch.tv/kraken/users?login={user['name']}"
        headers = {
            "Client-ID": bot.CLIENT_ID,
            "Accept": "application/vnd.twitchtv.v5+json",
        }
        resp = get(url,headers=headers).json()

        bot.send_message(f"{user['name']} Joined king of the hill")
        data = {
            'user': user,
            'args': args,
            'logo': resp['users'][0]['logo']
        }
        bot.PIPES['t2s']['data'].put(data)

def bbb(bot,user,*args):
    bot.send_message(f"Sending a BBB request {user['name']}!")
    file_name = None
    if len(args) == 1:
        for file in os.listdir('./sounds'):
            if args[0] == file[:-4]:
                file_name = file[:-4]
                # print(file_name, file[:-4])

    data = {
        'user': user,
        'filename':file_name
    }

    bot.PIPES['t2d']['bbb'].put(data)

def basilisk(bot,user,*args):
    if bot.hunt_flag == False and user['name'] == 'adeadzeplin':
        bot.send_message(f"Sending a basilisk request {user['name']}!")
        bot.hunt_flag = True
    elif len(args) == 1:
        data = {
            'user': user,
            'command': None
        }
        temp = args[0].lower()
        if temp in ['up','u','w']:
            data['command'] = 'w'
        elif temp in ['down','s']:
            data['command'] = 's'
        elif temp in ['right','r','d']:
            data['command'] = 'd'
        elif temp in ['left','l','a']:
            data['command'] = 'a'
        elif temp in ['0',')','@']:
            data['command'] = '0'
        elif user['name'] == 'adeadzeplin':
            data['command'] = args[0]

        if data['command'] == None:
            # bot.send_message(f"Sending a BBB request {user['name']}!")
            pass
        else:
            bot.PIPES['t2d']['hunt'].put(data)