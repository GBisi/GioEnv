import serial
from microbit import Microbit
import json


class Manager:


    def __init__(self, db, port):
        self.MICROBIT_PORT = port
        self.microbits = {}
        self.db = db

    def ReadSerial(self):
        with serial.Serial(self.MICROBIT_PORT, 115200) as s:
            print("connected")
            while True:
                byte = s.readline()
                line = json.loads(byte.decode().strip())
                try:
                    yield int(line["s"]), line["n"], int(line["v"])
                except:
                    pass


    def run(self):

        for serial_number, name, val in self.ReadSerial():
            if serial_number not in self.microbits:
                self. microbits[serial_number] = Microbit(serial_number)
                self.db.add_thing(self.microbits[serial_number])
            self.microbits[serial_number].update(name, val)