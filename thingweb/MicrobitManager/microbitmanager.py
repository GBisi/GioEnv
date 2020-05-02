import sys
sys.path.insert(0, "./")

from microbit import Microbit
from room import Room
import json
import sys
import requests

import configparser

from serial import Serial, SerialException

class MicrobitManager:

    def __init__(self, serialport, clientport, server, ip="127.0.0.1"):
        self.MICROBIT_PORT = serialport
        self.CLIENT_PORT = clientport
        self.SERVER = "http://"+server[0]+":"+str(server[1])+"/"
        self.microbits = {}
        self.rooms = {}

        print("MICROBIT MANAGER ONLINE @ "+ip+":"+str(clientport))
        print("MICROBIT MANAGER READ "+serialport)
        print("MICROBIT MANAGER SEND TO "+self.SERVER)


        self.add_thing(Room(42,'http://131.114.73.148:2000/tetoz','http://131.114.73.148:2000/puvit'))
        self.add_thing(Microbit(1252840479.9999999))
        self.add_thing(Microbit(384933164))
        

    def ReadSerial(self,timeout):
        try:
            with Serial(self.MICROBIT_PORT, 115200, timeout=timeout) as s:
                print("Serial: Connected!")
                while True:
                    try:
                        byte = s.readline()
                        if byte is None or byte == b'':
                            continue
                        byte = byte.decode().strip()
                        line = json.loads(byte)
                        #print("Serial:",line["s"],line["n"],line["v"])
                        yield int(line["s"]), line["n"], int(line["v"])
                    except ValueError:
                        print("Serial: Value Error:",byte)
        except SerialException:
             print("Serial: Not Connected!")

    def update(self,thing,prop,val):
        
        try:
            r = requests.patch(self.SERVER+thing+"/properties/"+prop,data=str(val))
            print("WoT: updated ", thing, r.status_code, r.text)
            return r.status_code,r.text
        except requests.ConnectionError:
            print("WoT Server: Connection Error")

    def add_thing(self, thing):
        try:
            td = thing.get_thing_description()
            r = requests.post(self.SERVER,data=json.dumps(td))
            if r.status_code != 201:
                print("WoT: not added ",td["thing"]["title"], r.status_code, r.text)
            else:
                print("WoT: added ",td["thing"]["title"], r.status_code)
            return r.status_code,r.text
        except requests.ConnectionError:
            print("WoT Server: Connection Error")
            return None

    def get_thing(self, thing):
        try:
            r = requests.get(self.SERVER+thing)
            if r.status_code != 200:
                print("WoT: not getted ",thing, r.status_code, r.text)
            else:
                print("WoT: getted ",thing, r.status_code)
            if r.status_code == requests.codes.ok:
                return r.json()
            return None
        except requests.ConnectionError:
            print("WoT Server: Connection Error")
            return None


    def run(self):
       with open('./rooms.json') as file:
            self.data = json.load(file)

            for serial_number, name, val in self.ReadSerial(None):
                
                if serial_number not in self.microbits:
                    self.microbits[serial_number] = Microbit(serial_number)
                    if self.get_thing(self.microbits[serial_number].get_friendly_name()) is None:
                        self.add_thing(self.microbits[serial_number])

                microbit = Microbit.get_microbit_name(serial_number)
                print("Serial: ",microbit,name,val)

                self.update(microbit,name,val)
                if microbit in self.data:
                    if name in self.data[microbit]:
                        for r in self.data[microbit][name]:
                            if r not in self.rooms:
                                self.rooms[r] = Room(r)
                            if self.get_thing(self.rooms[r].get_thing_description()["thing"]["title"]) is None:
                                if self.add_thing(self.rooms[r]) is None:
                                    print("Impossible to connect with Room "+r)
                                    continue;
                            self.update(self.rooms[r].get_thing_description()["thing"]["title"],name,val)


# python Desktop/WoT/clientmanager.py COM7 4201 127.0.0.1 4200

def configuration():

    config = configparser.ConfigParser()
    config.read('../../config.ini')

    test = config["TEST"].getboolean("TEST")

    if test:
        MY_IP = config["TEST"]["MY_IP"]
        SERVER_IP = config["TEST"]["MY_IP"]
    else:
        MY_IP = config["CLIENTMANAGER"]["MY_IP"]
        SERVER_IP = config["DEFAULT"]["MY_IP"]

    SERVER_PORT = int(config["WOT"]["WOT_PORT"])
    SERIAL_PORT = config["CLIENTMANAGER"]["SERIAL_PORT"]
    CLIENT_PORT = int(config["CLIENTMANAGER"]["CLIENT_PORT"])

    MicrobitManager(SERIAL_PORT,int(CLIENT_PORT),(str(SERVER_IP),int(SERVER_PORT)), ip=MY_IP).run()

if __name__ == "__main__":
    
    if len(sys.argv) != 6:
        print("microbitmanager [serial_port] [my_ip] [my_port] [server_ip] [server_port]")
        configuration()
    else:
        MicrobitManager(str(sys.argv[1]),int(sys.argv[3]),(str(sys.argv[4]),int(sys.argv[5])), ip=sys.argv[2]).run()
