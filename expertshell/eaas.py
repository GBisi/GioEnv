import sys
sys.path.insert(0, "../")
sys.path.insert(0, "../../")

import math 

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
                print("Request:",data["rules"],",",data["facts"])
                if type(data["rules"]) == list:
                    data["rules"] = str(data["rules"]).replace("'","")
                if type(data["facts"]) == list:
                    data["facts"] = str(data["facts"]).replace("'","")
                ans = expert.solve(data["facts"],data["rules"])
            else:
                ans = {"new_facts":data["facts"],"actions":"[]"}
        else:
            ans = {"new_facts":"[]","actions":"[]"}
        
        return jsonify(ans)
    
    abort(400)

@app.route('/prove', methods=['POST'])
def prove():

    data = request.get_json()
    
    if data is not None:

        ans = {}

        if not "conclusions" in data:
            return infer()       

        if "facts" in data and data["facts"] != "" and data["facts"] != "[]":
            if "rules" in data and data["rules"] != "" and data["rules"] != "[]":
                if type(data["rules"]) == list:
                    data["rules"] = str(data["rules"]).replace("'","")
                if type(data["facts"]) == list:
                    data["facts"] = str(data["facts"]).replace("'","")
                print("Request:",data["rules"],",",data["facts"])
                ans = expert.solve(data["facts"],data["rules"])
            else:
                abort(400)
        else:
            abort(400)

        del ans["actions"]
        ans["qed"] = False
        if type(data["conclusions"]) == str:
            data["conclusions"] = data["conclusions"][1:-1].split(',')
        ans["new_facts"] = ans["new_facts"][1:-1].split(', ')
        if set(data["conclusions"]).issubset(set(ans["new_facts"])):
            ans["qed"] = True

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

@app.route('/mediate/avg', methods=['POST'])
def get_avg():

    data = request.get_json()
    all_number = False
    if data is not None:

        if "data" in data and not "values" in data:
            all_number = True
            for d in data["data"]:
                if not isinstance(d, (int, float, complex)):
                    all_number = False
            
        if all_number:
            avg = sum(data["data"])/len(data["data"])
            if "rounding" in data:
                if data["rounding"] == "ceil":
                    avg=math.ceil(avg)
                elif data["rounding"] == "floor":
                    avg=math.floor(avg)
                elif data["rounding"] == "round":
                    avg=round(avg)
                else:
                    avg=round(avg)
            else:
                    avg=round(avg)

            return(jsonify({"avg":avg}))

        if "data" in data and "values" in data:
            if len(data["values"]) == 0:
               abort(400)
            if len(data["data"]) == 0:
                return(jsonify({"avg":data["values"][round((len(data["values"])/2))]}))
            i=0
            in_num=data["data"]
            for l in data["values"]:
                in_num=[i if x==l else x for x in in_num]
                i=i+1
            avg = (sum(in_num)/len(in_num))
            if "rounding" in data:
                if data["rounding"] == "ceil":
                    avg=math.ceil(avg)
                elif data["rounding"] == "floor":
                    avg=math.floor(avg)
                elif data["rounding"] == "round":
                    avg=round(avg)
                else:
                    avg=round(avg)
            else:
                    avg=round(avg)
            return(jsonify({"avg":data["values"][avg]}))
    
    abort(400)

@app.route('/mediate/min', methods=['POST'])
def get_min():

    data = request.get_json()
    all_number = False
    if data is not None:

        if "data" in data and not "values" in data:
            all_number = True
            for d in data["data"]:
                if not isinstance(d, (int, float, complex)):
                    all_number = False
            
        if all_number:
            return(jsonify({"min":min(data["data"])}))

        if "data" in data and "values" in data:
            if len(data["values"]) == 0:
               abort(400)
            if len(data["data"]) == 0:
                return(jsonify({"min":data["values"][0]}))
            for l in data["values"]:
                if l in data["data"]:
                    return(jsonify({"min":l}))
    
    abort(400)

@app.route('/mediate/max', methods=['POST'])
def get_max():

    data = request.get_json()
    all_number = False
    if data is not None:

        if "data" in data and not "values" in data:
            all_number = True
            for d in data["data"]:
                if not isinstance(d, (int, float, complex)):
                    all_number = False
            
        if all_number:
            return(jsonify({"max":max(data["data"])}))

        if "data" in data and "values" in data:
            if len(data["values"]) == 0:
                abort(400)
            if len(data["data"]) == 0:
                return(jsonify({"min":data["values"][0]}))
            for l in reversed(data["values"]):
                if l in data["data"]:
                    return(jsonify({"max":l}))
    
    abort(400)

@app.route('/mediate/most', methods=['POST'])
def get_most():

    data = request.get_json()
    if data is not None:
       if "data" in data and "values" in data:
            if len(data["values"]) == 0:
               data["values"] = data["data"]
            if len(data["data"]) == 0:
                return(jsonify({"most":"","occurences":0}))
            m=-1
            most = ""
            for l in data["values"]:
                x = data["data"].count(l)
                if x > m:
                    m=x
                    most = l
            if "quorum" in data:
                return(jsonify({"most":most,"occurences":m,"quorum":m >= data["quorum"]}))
            return(jsonify({"most":most,"occurences":m}))
    
    abort(400)

@app.route('/mediate', methods=['POST'])
def mediate():
    data = request.get_json()
    if "service" in data:
        if data["service"] == "avg":
            return get_avg()
        elif data["service"] == "min":
            return get_min()
        elif data["service"] == "max":
            return get_max()
        elif data["service"] == "most":
            return get_most()
        else:
            abort(404)
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
