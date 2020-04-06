from problog.program import PrologString
from problog.core import ProbLog
from problog import get_evaluatable
from problog.engine import DefaultEngine

from compiler import Compile
import json

class ExpertSystem:
    
    def __init__(self, rulebook):
        
       
       open(rulebook+".pl","w").write(Compile(rulebook+".txt"))
       self._rulebook = rulebook
       pass
    
    def solve(self, facts):

        query = """ 
        :- use_module(library(assert)).
        :- use_module(library(lists)).
        :- consult('expert.pl').
        :- consult('"""+self._rulebook+""".pl').
        query(compute("""+facts+""",X)).
        """

        p = PrologString(query)

        decisions = get_evaluatable().create_from(p).evaluate()

        print("decisions:",decisions)

        ans = str(decisions).split("],")
        ans = ans[1].split("):")

        if ans[0][0] == "[":
            return ans[0]
        else:
            return "[]"



if __name__ == "__main__":
    e = ExpertSystem("rules-es")
    print(e.solve("[temperature(very_low),light(high)]"))
