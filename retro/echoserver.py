import sys
import time
from mysocket import MySocket

class EchoServer:
    
    def __init__(self, ip, port, n=1, m=1, header = None, debug = False):

        if header is None:
            
            self.header = "\nEchoed by "+str(port)

        else:
            self.header = header

        self.socket = MySocket(port,n,m, ip=ip)
        self.debug = debug
        print("--- ECHO SERVER ONLINE AT PORT "+str(port)+" ---")


    def start(self, delta):
        print("--- ECHO SERVER START ---")
        self.socket.start()
        start = time.time()
        while time.time()-start < delta:

            msg = self.socket.receive()
            

            if msg is not None:
                if self.debug:
                    print(msg)
                self.socket.send(str(msg.get_data())+self.header,msg.get_sender())

        print("--- ECHO SERVER CLOSE ---")
    
if __name__ == "__main__":

    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("echoserver [ip] [port] [time] [[debug]]")
    elif len(sys.argv) == 4:
        EchoServer(str(sys.argv[1]),int(sys.argv[2])).start(int(sys.argv[3]))
    else:
        EchoServer(str(sys.argv[1]),int(sys.argv[2]),True).start(int(sys.argv[3]))

