import sys
import time
from mysocket import MySocket

class EchoServer:
    
    def __init__(self, ip, port, mblen=1, mbnum=1, header = None, debug = False):
        if header is None:
            self.header = "\nEchoed by "+str(port)
        else:
            self.header = header
        self.socket = MySocket(port,mblen,mbnum, ip=ip,debug=debug)
        self.debug = debug
        print("--- ECHO SERVER ONLINE AT PORT "+str(port)+" ---")


    def start(self, delta=0):
        print("--- ECHO SERVER START ---")
        self.socket.start()
        start = time.time()
        while delta == 0 or time.time()-start < delta:
            msg = self.socket.receive()
            if msg is not None:
                self.socket.send(str(msg.get_data())+self.header,msg.get_sender(),mailbox=msg.get_mailbox())
                if self.debug:
                    print("echoed:",msg)
        print("--- ECHO SERVER CLOSE ---")
    
if __name__ == "__main__":

    if len(sys.argv) != 6 and len(sys.argv) != 7:
        print("echoserver [ip] [port] [time] [mb_len] [mb_num] [[debug]]")
    elif len(sys.argv) == 6:
        EchoServer(str(sys.argv[1]),int(sys.argv[2]),int(sys.argv[4]),int(sys.argv[5]),header="").start(int(sys.argv[3]))
    else:
        EchoServer(str(sys.argv[1]),int(sys.argv[2]),int(sys.argv[4]),int(sys.argv[5]),header="",debug=True).start(int(sys.argv[3]))

