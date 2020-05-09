import serial


port = serial.Serial('COM7',115200)
with port as s:
    s.write('hello\n'.encode())