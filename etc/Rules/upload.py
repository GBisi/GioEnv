from os import listdir
from os.path import isfile, join
from s2mclient import S2MClient

s2m = S2MClient("http://131.114.73.148:2048/")

files = [f for f in listdir(".") if isfile(join(".", f))]

for f in files:

    chuncks = f.split("-")

    if len(chuncks) != 2 or chuncks[1] != "rules.txt":
        continue

    _,status_b = s2m.add_bucket(chuncks[0])
    if status_b == 201:
        print(chuncks[0],"created")
    data = open(f).read()
    _,status_a = s2m.add_obj(chuncks[0],"rules",data)
    if status_a == 201:
        print(chuncks[0]+"/rules created")
    else:
        _,status_u = s2m.update_obj(chuncks[0],"rules",data)
        if status_u == 200:
            print(chuncks[0]+"/rules updated")
        else:
            print("Error:","bucket",status_b,"add",status_a,"upload",status_u)

    
