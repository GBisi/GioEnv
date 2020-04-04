import sys
sys.path.insert(0, "../")
sys.path.insert(0, "../../")

from flask import Flask, request, abort
import json
import time
from flask_cors import CORS

from expertsystem import ExpertSystem

MY_IP = "131.114.73.148"
MY_IP = "127.0.0.1"

PORT = 1999
PREFIX = "http://"+MY_IP+":"+str(PORT)+"/"

app = Flask(__name__)
CORS(app)

es = ExpertSystem("rules-es")
superio = ExpertSystem("rules-superio")

@app.route('/', methods=['GET'])
def parse():

    data = request.get_json()
    
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

    req = req[:-1]+"]"

    print("parsing:",req)

    ans = "[]"

    if req != "[]":
        es_ans = es.solve(req)
        su_ans = superio.solve(req)
        print("es:",es_ans)
        print("superio:",su_ans)


    ans = "[]"

    print("answer:",ans)

    return ans

if __name__ == '__main__':
    print("IMM Server ONLINE @ "+MY_IP+":"+str(PORT))
    app.run(host=MY_IP,port=PORT)
