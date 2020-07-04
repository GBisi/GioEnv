import sys
sys.path.insert(0, "./")

from microbitmanager import *
import configparser
import random
import time

config = configparser.ConfigParser()
config.read('../../config.ini')

test = config["TEST"].getboolean("TEST")

if test:
    SERVER_IP = config["TEST"]["MY_IP"]
else:
    SERVER_IP = config["DEFAULT"]["MY_IP"]

SERVER_PORT = int(config["WOT"]["WOT_PORT"])
SERIAL_PORT = config["CLIENTMANAGER"]["SERIAL_PORT"]

mm = MicrobitManager(SERIAL_PORT,(str(SERVER_IP),int(SERVER_PORT)))

mm.add_thing(Room(270,"tetoz","tuvov"))
mm.add_thing(Microbit(1252840479.9999999))

for i in range(400):
    mm.update("room"+str(i),"light",random.randint(0,150))
    #mm.update("room"+str(i),"temperature",random.randint(20,23))