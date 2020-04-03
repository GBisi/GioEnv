import sys
import re

def write_rule(w,cf):
    w = w.replace(".","")
    w = w.replace("\n","")
    string = "rule( {} , {} ).".format(w,cf)
    print(string)
    return string

def write_ask(w):
    w = w.replace(".","")
    w = w.replace("\n","")
    string = "askable( {} ).".format(w)
    print(string)
    return string


def compile(file_name):
    text = "" 
    with open(file_name,"r") as file:
        for line in file: 
            cmd = line.split(" ")
            starter = cmd[0]

            if starter == "ASK":
                text = text + write_ask(cmd[1])+"\n"
            elif starter == "DEFINE":
                text = text + write_rule(cmd[1],100)+"\n"
            elif starter == "IF":
                cond = [cmd[1]]
                i = 2
                while cmd[i] != "THEN":
                    if cmd[i] == "and":
                        pass
                    else:
                        cond.append(cmd[i])
                    i = i+1
                i = i+1
                conc = cmd[i]
                conds = ""
                for c in cond:
                    conds = conds+", "+c
                string = "({} :- {})".format(conc,conds[1:])
                text = text + write_rule(string,100)+"\n"
            elif starter == "ANSWER":
                conc = cmd[1]
                conds = ""
                for c in list(filter(lambda a: a != "and", cmd[3:])):
                    conds = conds+", "+c
                string = "({} :- {})".format(conc,conds[1:])
                text = text + write_rule(string,100)+"\n"

    return text

if __name__ == "__main__":

    file_name = "rules.txt"
    output_file = "rulebook.pl"

    try:
        file_name = sys.argv[1]
    except:
        print("compiler.py [input] [output]")
        exit()

    try:
        output_file = sys.argv[2]
    except:
        print("compiler.py [input] [output]")
        exit()

    open(output_file,"w").write(compile(file_name))