import sys
sys.path.insert(0, "./")

from microbit import Microbit
from room import Room
import json
import sys
import requests

import configparser

from serial import Serial, SerialException

class ClientManager:

    def __init__(self, serialport, clientport, server, ip="127.0.0.1"):
        self.MICROBIT_PORT = serialport
        self.CLIENT_PORT = clientport
        self.SERVER = "http://"+server[0]+":"+str(server[1])+"/"

        self.microbit = {}
        self.rooms = {}

        print("MICROBIT MANAGER ONLINE @ "+ip+":"+str(clientport))
        print("MICROBIT MANAGER READ "+serialport)
        print("MICROBIT MANAGER SEND TO "+self.SERVER)

    def ReadSerial(self,timeout):
        try:
            with Serial(self.MICROBIT_PORT, 115200) as s:
                print("Serial: Connected!")
                while True:
                    try:
                        byte = s.readline()
                        byte = byte.decode().strip()
                        line = json.loads(byte)
                        print("Serial:",line["s"],line["n"],line["v"])
                        yield int(line["s"]), line["n"], int(line["v"])
                    except ValueError:
                        print("Serial: Value Error:",byte)
        except SerialException:
             print("Serial: Not Connected!")

    def update(self,thing,prop,val):
        
        try:
            r = requests.patch(self.SERVER+thing+"/properties/"+prop,data=str(val))
            return r.status_code,r.text
        except requests.ConnectionError:
            print("WoT Server: Connection Error")

    def add_thing(self, thing):
        try:
            td = thing.get_thing_description()
            r = requests.post(self.SERVER,data=json.dumps(td))
            return r.status_code,r.text
        except requests.ConnectionError:
            print("WoT Server: Connection Error")
            exit()


    def run(self):
       with open('./rooms.json') as file:
            self.data = json.load(file)
            
            for microbit in self.data:
                for attr in self.data[microbit]:
                    for n in self.data[microbit][attr]:
                        if n not in self.rooms:
                            self.rooms[n] = Room(n)
                            self.add_thing(self.rooms[n])

            for serial_number, name, val in self.ReadSerial(0):
                
                if serial_number not in self.microbits:
                    self.microbits[serial_number] = Microbit(serial_number)
                    self.add_thing(self.microbits[serial_number])

                microbit = Microbit.get_microbit_name(serial_number)
                self.update(microbit,name,val)
                if name in self.data[ microbit]:
                    for r in self.data[microbit][name]:
                        print(microbit,r,name)
                        self.update(self.rooms[r],name,val)


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

    ClientManager(SERIAL_PORT,int(CLIENT_PORT),(str(SERVER_IP),int(SERVER_PORT)), ip=MY_IP).run()

if __name__ == "__main__":
    
    if len(sys.argv) != 6:
        print("microbitmanager [serial_port] [my_ip] [my_port] [server_ip] [server_port]")
        configuration()
    else:
        ClientManager(str(sys.argv[1]),int(sys.argv[3]),(str(sys.argv[4]),int(sys.argv[5])), ip=sys.argv[2]).run()
