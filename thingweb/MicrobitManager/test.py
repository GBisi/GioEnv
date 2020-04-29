import requests
import sys
sys.path.insert(0, "./")
from microbit import Microbit
from room import Room
import json

uri = "http://131.114.73.148:2000/"

r = requests.get(uri)
print(r.status_code,r.text)
m = Room(42)
r = requests.post(uri,data=json.dumps(m.get_thing_description()))
from time import sleep
sleep(5)
print(r.status_code,r.text)