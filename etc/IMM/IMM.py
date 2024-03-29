import sys
sys.path.insert(0, "../")
sys.path.insert(0, "../../")

from flask import Flask, request, abort
import json
import time
from flask_cors import CORS

from expertsystem import ExpertSystem
from mediator import Mediator

app = Flask(__name__)
CORS(app)

es = ExpertSystem("rules-es")
superio = ExpertSystem("rules-superio")
io = Mediator("rules-io")

@app.route('/', methods=['GET'])
def parse():

    data = request.get_json()
    
    if data is not None:

        print("request:",data)

        req = "["

        if "tempL" in data:
            req = req+"temperature("+data["tempL"].lower()+"),"
        if "lightL" in data:
            req = req+"light("+data["lightL"].lower()+"),"
        if "outdoor_tempL" in data:
            req = req+"outdoor_temperature("+data["outdoor_tempL"].lower()+"),"
        if "outdoor_lightL" in data:
            req = req+"outdoor_light("+data["outdoor_lightL"].lower()+"),"

        if req == "[":
            return "[]"

        req = req[:-1]+"]"
        print("parsing:",req)
    
        es_ans = es.solve(req)
        su_ans = superio.solve(req)
        print("es:",es_ans)
        print("superio:",su_ans)
        med = io.mediate(es_ans,su_ans)
        print("mediating:",med)
        ans = med

        print("answer:",ans)

        return ans
    
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
    print("IMM Server ONLINE @ "+MY_IP+":"+str(PORT))
    app.run(host=MY_IP,port=PORT)
