from problog.program import PrologString
from problog.core import ProbLog
from problog import get_evaluatable
from problog.engine import DefaultEngine

from compiler import Compile
import json

class Mediator:
    
    def __init__(self, rulebook):
        
       
       open(rulebook+".pl","w").write(Compile(rulebook+".txt"))
       self._rulebook = rulebook
       
    
    def mediate(self, es, superio):

        query = """ 
        :- use_module(library(assert)).
        :- use_module(library(lists)).
        :- consult('mediator.pl').
        :- consult('"""+self._rulebook+""".pl').
        query(mediate("""+es+","+superio+""",X)).
        """

        p = PrologString(query)

        decisions = get_evaluatable().create_from(p).evaluate()

        print("decisions:",decisions)

        ans = str(decisions).split("],")
        ans = ans[2].split("):")

        if ans[0][0] == "[":
            return ans[0]
        else:
            return "[]"



if __name__ == "__main__":
    e = Mediator("rules-io")
    s = e.mediate("[set_temperature(high), set_light(high)]","[set_temperature(medium), set_temperature(medium)]")
    print(s)
