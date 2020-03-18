from mysocket import MySocket
import sys

class EchoServer:
    
    def __init__(self, port, n=1, m=1, header = None):

        if header is None:
            
            self.header = "\nEchoed by "+str(port)

        else:
            self.header = header

        self.socket = MySocket(port,n,m)

        print("--- ECHO SERVER ONLINE AT PORT "+str(port)+" ---")


    def start(self):
        print("--- ECHO SERVER START ---")
        self.socket.start()

        while True:

            msg = self.socket.receive()
            

            if msg is not None:
            
                self.socket.send(str(msg.get_data())+self.header,msg.get_sender())


    
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("echoserver [port]")
    else:
        EchoServer(sys.argv[1]).start()
