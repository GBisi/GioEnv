import serial
from microbit import Microbit
import json


class Manager:

    def __init__(self, db, port):
        self.MICROBIT_PORT = port
        self.microbits = {}
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

        for serial_number, name, val in self.ReadSerial():
            if serial_number not in self.microbits:
                self. microbits[serial_number] = Microbit(serial_number)
                self.db.add_thing(self.microbits[serial_number])
            self.microbits[serial_number].update(name, val)