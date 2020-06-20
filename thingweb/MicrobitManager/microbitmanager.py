import sys
sys.path.insert(0, "./")

from microbit import Microbit
from room import Room
from observer import Observer
from board import Board
import json
import sys
import requests
import time
import random

import configparser

from serial import Serial, SerialException

def update_dashboard(thing,prop,val):

    if prop == "light":
        val = int(100/255 * val)

    DashPy = "http://131.114.73.148:2042"
    try:
        requests.patch(DashPy+"/devices/"+thing+"/"+prop,json=float(val))
        print("Dashboard: updated",thing,prop)
    except:
        print("Dashboard: error",thing,prop)

class MicrobitManager:

    def __init__(self, serialport, server):
        self.MICROBIT_PORT = serialport
        self.SERVER = "http://"+server[0]+":"+str(server[1])+"/"
        self.microbits = {}
        self.rooms = {}

        print("MICROBIT MANAGER ONLINE")
        print("MICROBIT MANAGER READ "+serialport)
        print("MICROBIT MANAGER SEND TO "+self.SERVER)

        self.serial = Serial(self.MICROBIT_PORT, 115200)

        self.waiting = {} #microbit waiting confirmed
        self.approved = [] #approved microbit

    def ReadSerial(self,timeout):
        try:
            with self.serial as s:
                print("Serial: Connected!")
                while True:
                    try:
                        byte = s.readline()
                        if byte is None or byte == b'':
                            continue
                        byte = byte.decode().strip()
                        line = json.loads(byte)
                        token = line["n"].split("$")
                        #print(float(line["s"]), token[0], int(token[1]))
                        yield float(line["s"]), token[0], int(token[1])
                    except ValueError:
                        print("Serial: Value Error:",byte)
        except SerialException:
             print("Serial: Not Connected!")

    def update(self,thing,prop,val):

        if prop == "temp":
            prop = "temperature"

        update_dashboard(thing,prop,val)

        try:
            r = requests.patch(self.SERVER+thing+"/properties/"+prop,data=str(val))
            print("WoT: updated",prop, thing, r.status_code, r.text)
            return r.status_code,r.text
        except requests.ConnectionError:
            print("WoT Server: Connection Error")

    def add_thing(self, thing):
        try:
            td = thing.get_thing_description()
            r = requests.post(self.SERVER,data=json.dumps(td))
            if r.status_code != 201:
                print("WoT: not added",td["thing"]["title"], r.status_code, r.text)
            else:
                print("WoT: added",td["thing"]["title"], r.status_code)
            return r.status_code,r.text
        except requests.ConnectionError:
            print("WoT Server: Connection Error")
            return None

    def get_thing(self, thing):
        try:
            r = requests.get(self.SERVER+thing)
            if r.status_code != 200:
                print("WoT: not getted",thing, r.status_code, r.text)
            else:
                print("WoT: getted",thing, r.status_code)
            if r.status_code == requests.codes.ok:
                return r.json()
            return None
        except requests.ConnectionError:
            print("WoT Server: Connection Error")
            return None

    def make_microbit_observer(self, microbit):
        def callback(name):
            s = self.serial
            def f(state):
                try:
                    print(microbit+": ",state)
                    time.sleep(random.randint(1,10))
                    print(microbit+": sending temp")
                    s.write(("temp"+"$"+state["temperature"]+"$"+microbit+"\n").encode())
                    print(microbit+": sended temp")
                    time.sleep(10)
                    print(microbit+": sending light")
                    s.write(("light"+"$"+state["light"]+"$"+microbit+"\n").encode())
                    print(microbit+": sended light")
                except:
                    print(microbit+": Observer -> Serial ERROR")
            return f 
        Observer(self.SERVER+microbit+"/events/setup").start(callback(microbit),True)
        print("Observer: new",microbit,"observer")


    def run(self):
       with open('./rooms.json') as file:
            self.data = json.load(file)

            if self.get_thing("approved") is None:
                self.add_thing(Board("approved"))

            def approved(waiting,approved):

                def f(ads):
                    print("New ads:",ads)
                    if ads["microbit"] in waiting:
                        if ads["pass"] == waiting[ads["microbit"]]:
                            print("Approved:",ads["microbit"])
                            approved.append(ads["microbit"])

                return f

            Observer(self.SERVER+"approved/events/ads").start(approved(self.waiting,self.approved),True)

            rooms = {}
            for microbit in self.data:
                for name in self.data[microbit]:
                    for r in self.data[microbit][name]:
                        if r not in rooms:
                            rooms[r] = {}
                        if name == "ac":
                            rooms[r]["temperature"] = microbit
                        if name == "windows":
                            rooms[r]["light"] = microbit

            for r in rooms:
                self.rooms[r] = Room(r,rooms[r]["temperature"],rooms[r]["light"])
            
            for serial_number, name, val in self.ReadSerial(None):

                microbit = Microbit.get_microbit_name(serial_number)
                if name == "syn":
                    self.waiting[microbit] = str(val)
                    print("Now Waiting:",microbit,val)
                    print("Waiting List:",self.waiting)
                    continue;

                if microbit not in self.approved:
                    print("Waiting:",microbit)
                    #continue;

                if microbit in self.waiting:
                    del self.waiting[microbit]
                
                if serial_number not in self.microbits:
                    self.microbits[serial_number] = Microbit(serial_number)
                    self.make_microbit_observer(microbit)
                if self.get_thing(self.microbits[serial_number].get_friendly_name()) is None:
                    self.add_thing(self.microbits[serial_number])

                print("Serial: ",microbit,name,val)

                self.update(microbit,name,val)
                if microbit in self.data:
                    if name in self.data[microbit]:
                        for r in self.data[microbit][name]:
                            if self.get_thing(self.rooms[r].get_thing_description()["thing"]["title"]) is None:
                                if self.add_thing(self.rooms[r]) is None:
                                    print("Impossible to connect with Room "+str(r))
                                    update_dashboard(self.rooms[r].get_thing_description()["thing"]["title"],name,val)
                                    continue;
                            self.update(self.rooms[r].get_thing_description()["thing"]["title"],name,val)

# python Desktop/WoT/clientmanager.py COM7 4201 127.0.0.1 4200

def configuration():

    config = configparser.ConfigParser()
    config.read('../../config.ini')

    test = config["TEST"].getboolean("TEST")

    if test:
        SERVER_IP = config["TEST"]["MY_IP"]
    else:
        SERVER_IP = config["DEFAULT"]["MY_IP"]

    SERVER_PORT = int(config["WOT"]["WOT_PORT"])
    SERIAL_PORT = config["CLIENTMANAGER"]["SERIAL_PORT"]

    MicrobitManager(SERIAL_PORT,(str(SERVER_IP),int(SERVER_PORT))).run()

if __name__ == "__main__":
    
    if len(sys.argv) != 6:
        print("microbitmanager [serial_port] [server_ip] [server_port]")
        configuration()
    else:
        MicrobitManager(str(sys.argv[1]),(str(sys.argv[4]),int(sys.argv[5]))).run()
