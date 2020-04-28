import requests
import sys
sys.path.insert(0, "./")
from microbit import Microbit
import json

uri = "http://131.114.73.148:2000/"

r = requests.get(uri)
print(r.status_code,r.text)
m = Microbit(1252840479.9999999)
r = requests.post(uri,data=json.dumps(m.get_thing_description()))