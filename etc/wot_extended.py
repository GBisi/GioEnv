from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/things')
def parse_things():
    return "things"

@app.route('/things/<thing>')
def parse_thing(thing):
    return thing

@app.route('/things/<thing>/properties')
def parse_properties(thing):
    return thing+" "+"properties"

@app.route('/things/<thing>/properties/<prop>')
def parse_property(thing,prop):
    return thing+" "+"properties"+" "+prop

@app.route('/things/<thing>/events')
def parse_events(thing):
    return thing+" "+"events"

@app.route('/things/<thing>/events/<event>')
def parse_event(thing,event):
    return thing+" "+"events"+" "+event

@app.route('/things/<thing>/actions')
def parse_actions(thing):
    return thing+" "+"actions"

@app.route('/things/<thing>/actions/<action>')
def parse_action(thing,action):
    return thing+" "+"actions"+" "+action

@app.route('/things/<thing>/actions/<action>/<value>')
def action_request(thing,action,value):
    return thing+" "+"action_request"+" "+action+" "+value

if __name__ == '__main__':
    app.run(debug=True)
