import sys
sys.path.insert(0, "../")
sys.path.insert(0, "./src")

import serial
from microbit import Microbit
from room import Room
import json
import sys
from retro.mysocket import MySocket


class ClientManager:

    def __init__(self, serialport, retroport, server, ip="127.0.0.1"):
        self.MICROBIT_PORT = serialport
        self.RETRO_PORT = retroport
        self.SERVER = server
        self.socket = MySocket(retroport,1,100,ip=ip)

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
            packet = self.ReadSerial(1)
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

if __name__ == "__main__":
    
    if len(sys.argv) != 6:
        print("clientmanager [serial_port] [my_ip] [retro_port] [server_ip] [server_port]")
    else:
        ClientManager(str(sys.argv[1]),int(sys.argv[3]),(str(sys.argv[4]),int(sys.argv[5])), ip=sys.argv[2]).run()
