from flask import Flask, request, abort
from werkzeug.routing import BaseConverter
import threading
import json
import time
from flask_sockets import Sockets
from flask_cors import CORS

from microbitmanager import Manager
from database import Database

from gevent import pywsgi
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

MICROBIT_PORT = "COM7"
PREFIX = "http://localhost:4242/"

class Thing(BaseConverter):
    def to_python(self, value):
        thing = db.get_thing(value)
        if thing is None:
            abort(404)
        return thing

    def to_url(self, value):
        return value.get_id()

def perform_action(action):
    threading.Thread(target=action.start).start()

def get_actions(request, thing, name):
    return json.dumps(thing.get_action_descriptions(name))

def post_actions(request, thing, name):
    response = {}
    for action_name, params in request.items():
        input_ = None
        if 'input' in params:
            input_ = params['input']

        action = thing.perform_action(action_name, input_)

        if action:
            response.update(action.as_action_description())
            # Start the action
            perform_action(action)
            

    return response

def get_events(request, thing, name):
    return json.dumps(thing.get_event_descriptions(name))

def get_properties(request, thing, name):
    if name is None:
        return thing.get_properties()
    else:
        prop = thing.get_property(name)
        if prop is None:
            abort(404)
        else:
            return {name:prop}

def put_property(request, thing, name):
    if name is None:
        abort(404)
    if name not in request:
        abort(400)
    if thing.has_property(name):
        try:
            thing.set_property(name, request[name])
        except PropertyError:
            abort(400)

        return {
            name: thing.get_property(name)
        }
    else:
        self.set_status(404)

app = Flask(__name__)
CORS(app)
app.url_map.converters["thing"] = Thing
operations = {"properties":{"GET": get_properties, "PUT": put_property}, 
"events":{"GET": get_events},
"actions":{"GET": get_actions, "POST":post_actions}}

db = Database(PREFIX+"things/")
sockets = Sockets(app)


@app.route('/things')
def parse_things():
    return json.dumps([ob.as_thing_description() for ob in db.get_things()])

@app.route('/things/<thing:thing>')
def parse_thing(thing):
    return thing.as_thing_description()

@app.route('/things/<thing:thing>/<operation>', methods=['GET','POST'])
def parse_operations(thing,operation):
    return parse(request, thing, operation)

@app.route('/things/<thing:thing>/<operation>/<name>', methods=['GET', 'POST', 'PUT'])
def parse_operation(thing,operation,name):
    return parse(request, thing, operation, name)

@app.route('/things/<thing:thing>/actions/<name>/<id_>', methods=['GET', 'PUT', 'DELETE'])
def action_request(thing,name,id_):
    action = thing.get_action(name, id_)
    if action is None:
        abort(404)
    else:
        if request.method == 'GET':
            return action.as_action_description()
        elif request.method == 'PUT':
            abort(501, 'Not yet in the spec')
        elif request.method == 'DELETE':
            if thing.remove_action(name, id_):
                return '',204
            else:
                abort(404)

def parse(request, thing, operation, name=None):
    if (operation in operations) and (request.method in operations[operation]):
        return operations[operation][request.method](request.get_json(),thing,name)
    else:
        abort(400)

def on_socket_open(thing, ws):
    thing.add_subscriber(ws)

def on_socket_close(thing, ws):
    thing.remove_subscriber(ws)

def on_socket_message(thing, ws, message):
    try:
        message = json.loads(message)
    except ValueError:
        return json.dumps({
                    'messageType': 'error',
                    'data': {
                        'status': '400 Bad Request',
                        'message': 'Parsing request failed',
                    }})
    
    if 'messageType' not in message or 'data' not in message:
        return json.dumps({
            'messageType': 'error',
            'data': {
                'status': '400 Bad Request',
                'message': 'Invalid message',
                'request': message,
            }})

    msg_type = message['messageType']

    if msg_type == 'setProperty':
        for property_name, property_value in message['data'].items():

            try:
                thing.set_property(property_name, property_value)
            except PropertyError as e:
                return json.dumps({
                    'messageType': 'error',
                    'data': {
                        'status': '400 Bad Request',
                        'message': str(e),
                    },
                })

    elif msg_type == 'requestAction':
        for action_name, action_params in message['data'].items():
            input_ = None
            if 'input' in action_params:
                input_ = action_params['input']

            action = thing.perform_action(action_name, input_)
            if action:
                perform_action(action)
            else:
                return json.dumps({
                    'messageType': 'error',
                    'data': {
                        'status': '400 Bad Request',
                        'message': 'Invalid action request',
                        'request': message,
                    },
                })
    elif msg_type == 'addEventSubscription':
        for event_name in message['data'].keys():
            thing.add_event_subscriber(event_name, ws)
    else:
        return json.dumps({
                'messageType': 'error',
                'data': {
                    'status': '400 Bad Request',
                    'message': 'Unknown messageType: ' + msg_type,
                    'request': message,
                },
            })
    

@sockets.route('/things/<thing>')
def on_socket_connection(ws, thing):

    thing = db.get_thing(thing)
    if thing is None:
        ws.send(json.dumps({
                    'messageType': 'error',
                    'data': {
                        'status': '404 Not Found',
                    }}))


    on_socket_open(thing, ws)
    try:
        while not ws.closed:
            message = ws.receive()
            if message is not None:
                resp = on_socket_message(thing, ws, message)
                if resp is not None:
                    ws.send(resp)
    except WebSocketError:
        pass

    on_socket_close(thing, ws)

if __name__ == '__main__':
    threading.Thread(target=Manager(db,MICROBIT_PORT).run).start()
    server = pywsgi.WSGIServer(('localhost', 4242), app, handler_class=WebSocketHandler)
    server.serve_forever()
