import socket
import json
from itertools import cycle

UDP_IP = "127.0.0.1"
UDP_PORT = 4243
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
 
while False:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data = data.decode("utf-8").replace("\'", "\"")
    print("received message:", data)
    obj = json.loads(data)
    msg = {"channel":obj["channel"], "ack":obj["seq"], "from": [UDP_IP, UDP_PORT], "to": [UDP_IP, 4242]}
    print("sended message:", msg)
    sock.sendto(str(msg).encode(),(UDP_IP, 4242))


dic = {}



dic[1] = 1
dic[2] = 2

dict1 = cycle(dic)

print(next(dict1))
print(next(dict1))
print(next(dict1))
print(next(dict1))

