import sys
sys.path.insert(0, "../")
sys.path.insert(0, "./src")

import serial
from microbit import Microbit
from room import Room
import json
import sys
from retro.mysocket import MySocket

import configparser


class ClientManager:

    def __init__(self, serialport, retroport, server, ip="127.0.0.1"):
        self.MICROBIT_PORT = serialport
        self.RETRO_PORT = retroport
        self.SERVER = server
        self.socket = MySocket(retroport,1,1000,ip=ip)

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


    def run(self):
        self.socket.start()
        while True:
            packet = self.ReadSerial(0.5)
            if packet is not None:
                msg = None
                try:
                    msg = json.loads(packet.decode().strip())
                except:
                    print("error",packet)
                
                if msg is not None:
                    print("send:",msg)
                    self.socket.send(msg,self.SERVER)


# python Desktop/WoT/clientmanager.py COM7 4201 127.0.0.1 4200

def configuration():

    config = configparser.ConfigParser()
    config.read('../config.ini')

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
