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

@app.route('/compilerules', methods=['POST'])
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
    

    solve(
"""
:- use_module(library(assert)).
:- use_module(library(lists)).
:- use_module(library(apply)).

user(u11).
set(u11, R, temperature, very_high):- inRoom(u11,R), temperature(R, low).
set(u11, R, temperature, high):- inRoom(u11,R), temperature(R, low), outdoor_temperature(very_low).
set(u11, R, temperature, low) :- inRoom(u11,R), temperature(R, high), outdoor_temperature(very_high).
set(u11, R, light, medium) :- inRoom(u11,R), light(R, low), outdoor_light(medium).
set(u11, R, light, high) :- inRoom(u11,R), light(R, low), outdoor_light(low).
user(u12).
set(u12, R, temperature, medium) :- inRoom(u12,R), temperature(R, low).
temperature(room1, low).
outdoor_temperature(very_high).
light(room1,low).
outdoor_light(high).
inRoom(u11, room1).
inRoom(u12, room1).
inRoom(u21, room2).
room(room1).
room(room2).
actuator(tetoz,temperature,room1).
actuator(tetoz,temperature,room2).
actuator(tuvov,light,room1).

go :- 
	findall((A,Type),actuator(A,Type,_),As),
	sort(As,SAs),
	decideActions(SAs).
decideActions([]).
decideActions([(A,Type)|As]) :-
        findall((U,A,Type,V), (user(U),inRoom(U,R),actuator(A,Type,R),set(U,R,Type,V)), UATVs),
	decideAction(UATVs),
      	decideActions(As).
decideAction([]).
decideAction([X|Xs]) :- mediate([X|Xs],A),assertz(A).
mediate(UATVs,todo(A,Type,V)) :- member((U,A,Type,V),UATVs), headOfDpt(U).			
headOfDpt(gf).
mediate(UATVs,todo(A,temperature,very_high)) :- member((_,A,temperature,very_high),UATVs). 	
mediate([(U,A,Type,V)|UATVs],todo(A,Type,W)) :-
	getStats([(U,A,Type,V)|UATVs],Stats),
    	getMax(Stats,(W,_)).       
getStats([],[]).
getStats([(_,_,_,T)|L], SS) :- getStats(L,S), add(T,S,SS).
add(T,[],[(T,1)]).
add(T,[(T,N)|L], [(T,NewN)|L]) :- NewN is N+1.
add(T,[(T1,N1)|L], [(T1,N1)|NewL]) :- T \== T1, add(T,L,NewL).
getMax([(V,N)|L],M) :- myGetMax((V,N),L,M).
myGetMax((V,N),[],(V,N)).
myGetMax((V,N),[(_,N1)|L],M) :- N>=N1, myGetMax((V,N),L,M).
myGetMax((_,N),[(V1,N1)|L],M) :- N<N1, myGetMax((V1,N1),L,M).
""","""""",["go.","todo(A,B,C)."]
)

    configuration()
    print("EaaS ONLINE @ "+MY_IP+":"+str(PORT))
    app.run(host=MY_IP,port=PORT)

