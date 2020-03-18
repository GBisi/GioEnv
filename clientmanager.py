import serial
from microbit import Microbit
from room import Room
import json
import sys
from retro.mysocket import MySocket


class ClientManager:

    def __init__(self, serialport, retroport, server):
        self.MICROBIT_PORT = serialport
        self.RETRO_PORT = retroport
        self.SERVER = server
        self.socket = MySocket(retroport,1,100)

    def ReadSerial(self):
        try:
            with serial.Serial(self.MICROBIT_PORT, 115200) as s:
                print("Serial: connected")
                while True:
                    try:
                        byte = s.readline()
                        yield byte
                    except:
                        pass
        except:
             print("Serial: not connected")


    def run(self):
        self.socket.start()
        for packet in self.ReadSerial():
            msg = json.loads(packet.decode().strip())
            print("send:",msg)
            self.socket.send(msg,self.SERVER)


# python Desktop/WoT/clientmanager.py COM7 4201 127.0.0.1 4200

if __name__ == "__main__":
    
    if len(sys.argv) != 5:
        print("clientmanager [serial_port] [retro_port] [server_ip] [server_port]")
    else:
        ClientManager(str(sys.argv[1]),int(sys.argv[2]),(str(sys.argv[3]),int(sys.argv[4]))).run()
