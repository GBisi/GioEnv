import serial
from microbit import Microbit
from room import Room
import json


class Manager:

    def __init__(self, db, port):
        self.MICROBIT_PORT = port
        self.microbits = {}
        self.rooms = {}
        self.db = db

    def ReadSerial(self):
        try:
            with serial.Serial(self.MICROBIT_PORT, 115200) as s:
                print("Serial: connected")
                while True:
                    try:
                        byte = s.readline()
                        line = json.loads(byte.decode().strip())
                        yield int(line["s"]), line["n"], int(line["v"])
                    except:
                        pass
        except:
             print("Serial: not connected")


    def run(self):

        with open('rooms.json') as file:
            self.data = json.load(file)
        
        for microbit in self.data:
            for n in self.data[microbit]:
                if n not in self.rooms:
                    self.rooms[n] = Room(n)
                    self.db.add_thing(self.rooms[n])

        for serial_number, name, val in self.ReadSerial():
            if serial_number not in self.microbits:
                self.microbits[serial_number] = Microbit(serial_number)
                self.db.add_thing(self.microbits[serial_number])

            self.microbits[serial_number].update(name, val)
            for r in self.data[Microbit.get_microbit_name(serial_number)]:
                self.rooms[r].update(name,val)
