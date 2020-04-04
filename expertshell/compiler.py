import sys
import re

def write_rule(w):
    w = w.replace(".","")
    w = w.replace("\n","")
    string = "rule({}).".format(w)
    return string

def write_ask(w):
    w = w.replace(".","")
    w = w.replace("\n","")
    string = "askable( {} ).".format(w)
    return string


def Compile(file_name):
    text = "" 
    with open(file_name,"r") as file:
        for line in file: 
            cmd = line.split(" ")
            starter = cmd[0]

            if starter == "ASK":
                text = text + write_ask(cmd[1])+"\n"
            elif starter == "DEFINE":
                text = text + write_rule(cmd[1])+"\n"
            elif starter == "IF":
                cond = [cmd[1]]
                i = 2
                while cmd[i] != "THEN" and cmd[i] != "DO":
                    if cmd[i] == "and":
                        pass
                    else:
                        cond.append(cmd[i])
                    i = i+1
                token = cmd[i]
                i = i+1
                conc = cmd[i]
                conds = ""
                for c in cond:
                    conds = conds+", "+c
                if token == "DO":
                    string = "[{} ] , do({})".format(conds[1:],conc)
                else:
                    string = "[{} ] , fact({})".format(conds[1:],conc)
                text = text + write_rule(string)+"\n"
            elif starter == "ANSWER":
                conc = cmd[1]
                conds = ""
                for c in list(filter(lambda a: a != "and", cmd[3:])):
                    conds = conds+", "+c
                string = "[{} ] , {}".format(conds[1:],conc)
                text = text + write_rule(string)+"\n"

    return text

if __name__ == "__main__":

    file_name = "rules.txt"
    output_file = "rulebook.pl"

    try:
        file_name = sys.argv[1]
    except:
        print("compiler.py [input] [output]")

    try:
        output_file = sys.argv[2]
    except:
        print("compiler.py [input] [output]")

    open(output_file,"w").write(compile(file_name))