from aiohttp import web
import socketio
import eventlet
import random
sio = socketio.Server()



class dataServer():
    def __init__(self):
        self.data_queue = None
        self.app =socketio.WSGIApp(sio)
service = dataServer()

@sio.event
def connect(sid, environ):
    print('Client connected ')
    sio.emit('init')

@sio.on('req')
def on_message(sid):
    try:
        out_data = service.data_queue['t2s']['data'].get(0)
        print('data being sent to client')
    except:
        out_data = 'None'
    sio.emit('chat_data',out_data)

@sio.event
def disconnect():
    print('Client disconnect')


def data_server(q):
    print('data server starting')
    service.data_queue = q
    eventlet.wsgi.server(eventlet.listen(('', 3333)), service.app, log_output=False)

if __name__ == '__main__':
    data_server(None)