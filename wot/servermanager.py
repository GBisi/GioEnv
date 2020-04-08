import serial
from microbit import Microbit
from room import Room
import json
import sys
from retro.mysocket import MySocket


class ServerManager:

    def __init__(self, db, ip, retroport):
        self.RETRO_PORT = retroport
        self.socket = MySocket(retroport,1,1000,ip=ip)
        self.microbits = {}
        self.rooms = {}
        self.db = db

        print("SERVER MANAGER ONLINE @ "+ip+":"+str(retroport))

    def ReadSocket(self):
        while True:
            msg = self.socket.receive()
            if msg is not None:
                line = msg.get_data()
                yield line["s"], line["n"], int(line["v"])

    def run(self):
        self.socket.start()
        print("Socket: connected")
        with open('../rooms.json') as file:
            self.data = json.load(file)
        
        for microbit in self.data:
            for attr in self.data[microbit]:
                for n in self.data[microbit][attr]:
                    if n not in self.rooms:
                        self.rooms[n] = Room(n)
                        self.db.add_thing(self.rooms[n])

        for serial_number, name, val in self.ReadSocket():
            
            if serial_number not in self.microbits:
                self.microbits[serial_number] = Microbit(serial_number)
                self.db.add_thing(self.microbits[serial_number])

            self.microbits[serial_number].update(name, val)
            microbit = Microbit.get_microbit_name(serial_number)
            if name in self.data[ microbit]:
                for r in self.data[microbit][name]:
                    print(microbit,r,name)
                    self.rooms[r].update(name,val)