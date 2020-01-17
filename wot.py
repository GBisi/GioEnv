from flask import Flask, jsonify, request, abort
from werkzeug.routing import BaseConverter
import threading
import json

from database import Database

class Thing(BaseConverter):
    def to_python(self, value):
        thing = db.get_thing('localhost:5000/things/'+value)
        if thing is None:
            abort(404)
        return thing

    def to_url(self, value):
        return value.get_id()

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
            threading.Thread(target=action.start).start()
            

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
            name: thing.get_property(name),
        }
    else:
        self.set_status(404)

app = Flask(__name__)
app.url_map.converters["thing"] = Thing
operations = {"properties":{"GET": get_properties, "PUT": put_property}, 
"events":{"GET": get_events},
"actions":{"GET": get_actions, "POST":post_actions}}

db = Database()
db.init()

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
            abort(500, 'Not yet in the spec')
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


if __name__ == '__main__':
    app.run()
