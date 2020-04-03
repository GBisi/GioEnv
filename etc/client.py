import socketio
import json
sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

sio.connect('http://localhost:5000','webthing')
sio.emit({"ciao":"hello"}, json=True)
print("sended")
while True:
    pass
sio.disconnect()