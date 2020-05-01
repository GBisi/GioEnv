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

        if "facts" in data:
            if "rules" in data:
                ans = expert.solve(data["facts"],data["rules"])
            else:
                ans = expert.solve(data["facts"])
        
        return ans
    
    abort(400)

@app.route('/parse/rulestolist', methods=['POST'])
def parse():

    data = request.get_json()
    
    if data is not None:
        print(data)
        ls = CompileList(data["rules"])
        print(ls)
        return jsonify({"rules":ls})
    
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
