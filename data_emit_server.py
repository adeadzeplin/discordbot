import asyncio
import aiohttp
from aiohttp import web
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

class dataServer():
    def __init__(self):
        self.data_queue = None

service = dataServer()

@sio.event
async def connect(sid, environ):
    print('Client connected ')
    await sio.emit('init')

@sio.on('req')
async def on_message(sid):
    try:
        out_data = service.data_queue['t2s']['data'].get_nowait()
    except:
        out_data = 'None'
    await sio.emit('chat_data', out_data)

@sio.on('insult')
async def on_message(sid):
    import insult
    out_data = {
        'insult': insult.insult(formated=False, adjmax=2, article=False)
    }
    await sio.emit('insult', out_data)

@sio.on('bbb')
async def on_message(sid, data):
    to_discord_bot = {
        'filename': data
    }
    service.data_queue['s2d']['bbb'].put_nowait(to_discord_bot)

@sio.event
async def disconnect(sid):
    print('Client disconnect')

async def data_server(q, port=3333):
    print('data server starting')
    service.data_queue = q
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    print(f"Server started at http://localhost:{port}")
    await asyncio.Event().wait()  # run forever

if __name__ == '__main__':
    asyncio.run(data_server(None))