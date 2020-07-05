import sys
sys.path.insert(0, "./")

from microbitmanager import *
import configparser
import random
import time
from mediator import Mediator

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
mm.add_thing(Room(271,"tetoz","gezev"))

mm.add_thing(Mediator())
mm.add_thing(Microbit(1252840479.9999999))
mm.add_thing(Microbit(384933164))
mm.add_thing(Microbit(671265031))
mm.add_thing(Microbit(20458004765.9999998))