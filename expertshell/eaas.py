import sys
sys.path.insert(0, "../")
sys.path.insert(0, "../../")

from flask import Flask, request, abort, jsonify
import json
import time
from flask_cors import CORS

from expertsystem import ExpertSystem

from rulescompiler import CompileList

import configparser

app = Flask(__name__)
CORS(app)
expert = ExpertSystem()

@app.route('/infer', methods=['POST'])
def infer():

    data = request.get_json()
    
    if data is not None:

        ans = {}       

        if "facts" in data and data["facts"] != "" and data["facts"] != "[]":
            if "rules" in data and data["rules"] != "" and data["rules"] != "[]":
                ans = expert.solve(data["facts"],data["rules"])
            else:
                ans = {"new_facts":data["facts"],"actions":"[]"}
        else:
            ans = {"new_facts":"[]","actions":"[]"}
        
        return jsonify(ans)
    
    abort(400)

@app.route('/parse/rulestolist', methods=['POST'])
def rulestolist():

    data = request.get_json()
    
    if data is not None:
        print(data)
        ls = CompileList(data["rules"])
        print(ls)
        return jsonify({"rules":ls})
    
    abort(400)

def JSONtoList(json):
    text = "["

    for key in json:
        if type(json[key]) == dict:
            text = text + key+"("+JSONtoList(json[key])+"),"
        else:
            text = text + key+"("+str(json[key])+"),"

    text = text[:-1] + "]"
    return text

@app.route('/parse/jsontolist', methods=['POST'])
def jsontolist():

    data = request.get_json()
    arr = []
    if data is not None:
       return jsonify({"text":JSONtoList(data)})
    
    abort(400)

def configuration():
    global MY_IP
    global PORT
    global PREFIX

    config = configparser.ConfigParser()
    config.read('../config.ini')

    test = config["TEST"].getboolean("TEST")

    if test:
        MY_IP = config["TEST"]["MY_IP"]
    else:
        MY_IP = config["DEFAULT"]["MY_IP"]

    PORT = int(config["MEDIATOR"]["PORT"])
    
    PREFIX = "http://"+MY_IP+":"+str(PORT)+"/"
    

if __name__ == '__main__':
    
    configuration()
    print("EaaS ONLINE @ "+MY_IP+":"+str(PORT))
    app.run(host=MY_IP,port=PORT)
