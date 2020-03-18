import sys
import time
from mysocket import MySocket

class EchoServer:
    
    def __init__(self, port, n=1, m=1, header = None):

        if header is None:
            
            self.header = "\nEchoed by "+str(port)

        else:
            self.header = header

        self.socket = MySocket(port,n,m)

        print("--- ECHO SERVER ONLINE AT PORT "+str(port)+" ---")


    def start(self, delta):
        print("--- ECHO SERVER START ---")
        self.socket.start()
        start = time.time()
        while time.time()-start < delta:

            msg = self.socket.receive()
            

            if msg is not None:
            
                self.socket.send(str(msg.get_data())+self.header,msg.get_sender())

        print("--- ECHO SERVER CLOSE ---")
    
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("echoserver [port] [time]")
    else:
        EchoServer(int(sys.argv[1])).start(int(sys.argv[2]))
