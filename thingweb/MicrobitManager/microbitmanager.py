import sys
sys.path.insert(0, "./")

import serial
from microbit import Microbit
from room import Room
import json
import sys
import requests

import configparser


class ClientManager:

    def __init__(self, serialport, retroport, server, ip="127.0.0.1"):
        self.MICROBIT_PORT = serialport
        self.RETRO_PORT = retroport
        self.SERVER = server

        print("CLIENT MANAGER ONLINE @ "+ip+":"+str(retroport))
        print("CLIENT MANAGER READ "+serialport)
        print("CLIENT MANAGER SEND TO "+str(server))

    def ReadSerial(self,timeout):
        with serial.Serial(self.MICROBIT_PORT, 115200,timeout=timeout) as s:
            #print("read")
            byte = s.readline()
            #print("byte",byte)
            if byte is not None and byte != b'':
                return byte
            return None

    def update(self,thing,prop,val):
        
        r = requests.patch(self.SERVER+thing+"/properties/"+prop,data=str(val))
        return r.status_code,r.text

    def add_thing(self, thing):

        td = thing.get_thing_description()
        r = requests.post(self.SERVER,data=json.dumps(td))
        return r.status_code,r.text


    def run(self):
       with open('./rooms.json') as file:
            self.data = json.load(file)
        
            for microbit in self.data:
                for attr in self.data[microbit]:
                    for n in self.data[microbit][attr]:
                        if n not in self.rooms:
                            self.rooms[n] = Room(n)
                            self.add_thing(self.rooms[n])

            for serial_number, name, val in self.ReadSocket():
                
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

    SERVER_PORT = int(config["WOT"]["RETRO_PORT"])
    SERIAL_PORT = config["CLIENTMANAGER"]["SERIAL_PORT"]
    RETRO_PORT = int(config["CLIENTMANAGER"]["RETRO_PORT"])

    ClientManager(SERIAL_PORT,int(RETRO_PORT),(str(SERVER_IP),int(SERVER_PORT)), ip=MY_IP).run()

if __name__ == "__main__":
    
    if len(sys.argv) != 6:
        print("clientmanager [serial_port] [my_ip] [retro_port] [server_ip] [server_port]")
        configuration()
    else:
        ClientManager(str(sys.argv[1]),int(sys.argv[3]),(str(sys.argv[4]),int(sys.argv[5])), ip=sys.argv[2]).run()
