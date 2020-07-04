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


print(Compile("""
IF temperature(very_low) and ( blue or green ) THEN do(temperature(low)).
IF temperature(low) and outdoor_temperature(medium) THEN do(temperature(medium)).
IF temperature(low) and outdoor_temperature(low) THEN do(temperature(medium)).
IF temperature(low) or outdoor_temperature(very_low) THEN do(temperature(medium)).
IF temperature(high) and outdoor_temperature(medium) THEN do(temperature(medium)).
IF temperature(high) and outdoor_temperature(high) THEN do(temperature(medium)).
IF temperature(high) and outdoor_temperature(very_high) THEN do(temperature(medium)).
IF temperature(very_high) THEN do(temperature(high)).

IF light(low) and outdoor_light(medium) THEN do(light(medium)).
IF light(low) and outdoor_light(low) THEN do(light(medium)).
IF light(medium) and outdoor_light(low) THEN do(light(high)).
IF light(medium) and outdoor_light(high) THEN do(light(low)).
IF light(high) and outdoor_light(high) THEN do(light(medium)).
IF light(high) and outdoor_light(medium) THEN do(light(medium)).

"""))