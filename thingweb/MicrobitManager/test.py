from serial import Serial, SerialException
import json
from microbit import Microbit

with Serial("COM7", 115200, timeout=None) as s:
    print("Serial: Connected!")
    while True:
        try:
            byte = s.readline()
            if byte is None or byte == b'':
                continue
            byte = byte.decode().strip()
            line = json.loads(byte)
            print("Serial:",line["s"],Microbit.get_microbit_name(line["s"]),line["n"],line["v"])
        except ValueError:
            print("Serial: Value Error:",byte)