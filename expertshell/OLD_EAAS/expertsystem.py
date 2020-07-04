from problog.program import PrologString
from problog.core import ProbLog
from problog import get_evaluatable
from problog.engine import DefaultEngine
from problog.tasks import sample

from rulescompiler import FileCompile
import json

class ExpertSystem:

    _expert_code = "expertB.pl"
    _expert_cmd = "expert" 
    
    def __init__(self, rulebook=None):
        
       self._rulebook = rulebook

       if rulebook is not None:
            open(rulebook+".pl","w").write(FileCompile(rulebook+".txt"))
    
    def solve(self, facts, rules = None):

        query = """ 
            :- use_module(library(assert)).
            :- use_module(library(lists)).
            :- use_module(library(apply)).
            :- consult('"""+ExpertSystem._expert_code+"""').

            """

        if rules is None and self._rulebook is not None:
            query = query+ """ 
            :- consult('"""+self._rulebook+""".pl').

            query("""+ExpertSystem._expert_cmd+"""("""+facts+""",N,R)).
            """

            decisions = self.query(query)

            ans = str(decisions).split("):")
            ans = ans[0].split("{"+ExpertSystem._expert_cmd+"(")

            ans = ans[1].split("],[")

            ans = {
                "new_facts":"["+ans[1]+"]",
                "actions":"["+ans[2]
            }

        if rules is not None:
            query = query+ """
            query("""+ExpertSystem._expert_cmd+"""("""+rules+""","""+facts+""",N,R)).
            """
            decisions = self.query(query)

            ans = str(decisions).split("):")
            ans = ans[0].split("],[")

            ans = {
                "actions":"["+ans[-1],
                "new_facts":"["+ans[-2]+"]"
            }

            print("Ans:",json.dumps(ans))
        
        return ans
        


    def query(self, query):

        p = PrologString(query)

        decisions = get_evaluatable().create_from(p).evaluate()
        
        return decisions



if __name__ == "__main__":
    e = ExpertSystem()
    print("Solution:",e.solve("[temperature(very_low),light(high)]","[ rule([ temperature(very_low) ] , [ do(set_temperature(high)) ]), rule([ temperature(low), outdoor_temperature(very_low) ] , [ do(set_temperature(high)) ]), rule([ temperature(high), outdoor_temperature(very_high) ] , [ do(set_temperature(low)) ]), rule([ temperature(very_high) ] , [ do(set_temperature(low)) ]), rule([ light(low), outdoor_light(medium) ] , [ do(set_light(medium)) ]), rule([ light(low), outdoor_light(low) ] , [ do(set_light(high)) ]), rule([ light(medium), outdoor_light(low) ] , [ do(set_light(high)) ]), rule([ light(medium), outdoor_light(high) ] , [ do(set_light(medium)) ]), rule([ light(high), outdoor_light(high) ] , [ do(set_light(medium)) ]), rule([ light(high), outdoor_light(medium) ] , [ do(set_light(medium)) ]) ]"))
