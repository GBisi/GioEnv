import sys
sys.path.insert(0, "../")
sys.path.insert(0, "../../")

import math 

from flask import Flask, request, abort, jsonify
import json
import time
from flask_cors import CORS

from problog.program import PrologString
from problog.core import ProbLog
from problog import get_evaluatable
from problog.engine import DefaultEngine
from problog.tasks import sample

import configparser

from Compiler import Compile

MY_IP = "127.0.0.1"
PORT = 5000

app = Flask(__name__)
CORS(app)

def solve(facts, policies, goals):
    query = (facts+"\n"+policies+"\n").replace(".",".\n")

    for g in goals:
        query += "query("+g.replace(".","")+").\n"

    print("Query:",query)

    p = PrologString(query)

    decisions = get_evaluatable().create_from(p).evaluate()

    print("Decisions:",decisions)

    ls = []

    for k,v in decisions.items():
        if v != 0:
            ls.append(str(k))

    return ls
    

def unroll(ls):

    txt = ""
    for i in ls:
        txt += i
    return txt

def roll(txt):
    ls = []
    txt = txt.split(".")
    for i in txt:
        if i != "":
            ls.append(i+".")
    return ls

@app.route('/decide', methods=['POST'])
def infer():

    data = request.get_json()
    
    if data is not None:

        ans = {"decisions":[]}       

        if "facts" in data and (data["facts"] != "" or data["facts"] != []):
            if "policies" in data and (data["policies"] != "" or data["policies"] != []):
                if "goals" in data and (data["goals"] != ""  or data["goals"] != []):
                    print("Request:",data["facts"],"\b",data["policies"],"\n",data["goals"])
                    if type(data["facts"]) == list:
                        data["facts"] = unroll(data["facts"])
                    if type(data["policies"]) == list:
                        data["policies"] = unroll(data["policies"])
                    if type(data["goals"]) == str:
                        data["goals"] = roll(data["goals"])
                    ans["decisions"] = solve(data["facts"],data["policies"],data["goals"])
                
        
        return jsonify(ans)
    
    abort(400)

@app.route('/parse/compilerules', methods=['POST'])
def compilerules():

    data = request.get_json()
    
    if data is not None:
        print(data)
        ls = Compile(data["rules"])
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

