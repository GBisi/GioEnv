import sys
import re

def write_rule(w):
    w = w.replace(".","")
    w = w.replace("\n","")
    string = "rule({}).".format(w)
    return string

def Compile(file_name):
    text = "" 
    with open(file_name,"r") as file:
        for line in file: 
            cmd = line.split(" ")
            starter = cmd[0]

            if starter == "IF":
                cond = [cmd[1]]
                i = 2
                while cmd[i] != "THEN":
                    if cmd[i] == "and":
                        pass
                    else:
                        cond.append(cmd[i])
                    i = i+1
                token = cmd[i]
                i = i+1
                conc = []
                while i<len(cmd):
                    if cmd[i] == "and":
                        pass
                    else:
                        conc.append(cmd[i])
                    i=i+1
                conds = ""
                concs = ""
                for c in cond:
                    conds = conds+", "+c
                for c in conc:
                    concs = concs+", "+c
                string = "[{} ] , [{} ]".format(conds[1:],concs[1:])
                text = text + write_rule(string)+"\n"

    return text


def CompileList(file_name):
    text = Compile(file_name)

    text = "[ "+ text.replace(".\n",", ")[:-2]+" ]"

    return text

if __name__ == "__main__":

    file_name = "rules-es.txt"
    output_file = "rulebook.pl"

    try:
        file_name = sys.argv[1]
    except:
        print("compiler.py [input] [output]")

    try:
        output_file = sys.argv[2]
    except:
        print("compiler.py [input] [output]")

    open(output_file,"w").write(Compile(file_name))
    print(CompileList(file_name))