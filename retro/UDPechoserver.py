import sys
import time
import socket

class EchoServer:
    
    def __init__(self, ip, port, debug = False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug = debug
        self.socket.bind((ip, port))
        print("--- ECHO SERVER ONLINE AT PORT "+str(port)+" ---")


    def start(self, delta=0):
        print("--- ECHO SERVER START ---")
        start = time.time()
        while delta == 0 or time.time()-start < delta:
            data, addr = self.socket.recvfrom(1024) # buffer size is 1024 bytes
            if data is not None:
                self.socket.sendto(data,addr)
                if self.debug:
                    print("echoed:",data)
        print("--- ECHO SERVER CLOSE ---")
    
if __name__ == "__main__":

    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("echoserver [ip] [port] [time] [[debug]]")
    elif len(sys.argv) == 6:
        EchoServer(str(sys.argv[1]),int(sys.argv[2])).start(int(sys.argv[3]))
    else:
        EchoServer(str(sys.argv[1]),int(sys.argv[2]),debug=True).start(int(sys.argv[3]))

