def Compile(file):
    file = file.replace(".","\n").lower()
    txt = ""
    for line in file.split('\n'): 
        print("line:",line)
        cmd = line.split(" ")

        rule = ""

        starter = cmd[0]

        if starter == "if":
            rule += " :- "
            i = 1
            while cmd[i] != "then":
                if cmd[i] == "and":
                    rule += ", "
                elif cmd[i] == "or":
                    rule += "; "
                else:
                    rule += cmd[i]
                i = i+1
            rule = cmd[i+1]+rule
        if rule != "":
            txt += rule+".\n"
    return txt
