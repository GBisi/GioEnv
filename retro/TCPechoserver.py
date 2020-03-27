import sys
import time
import socket

class EchoServer:
    
    def __init__(self, ip, port, debug = False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug = debug
        self.socket.bind((ip, port))
        self.socket.listen(1)
        print("--- ECHO SERVER ONLINE AT PORT "+str(port)+" ---")


    def start(self, delta=0):
        print("--- ECHO SERVER START ---")
        start = time.time()
        while delta == 0 or time.time()-start < delta:
            connection, client_address = self.socket.accept()
            data = connection.recv(16)
            if self.debug:
                print('received:',data)
            if data:
                if self.debug:
                    print('sending data back to the client')
                connection.sendall(data)
                connection.close()
            else:
                break     
        print("--- ECHO SERVER CLOSE ---")
    
if __name__ == "__main__":

    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("echoserver [ip] [port] [time] [[debug]]")
    elif len(sys.argv) == 4:
        EchoServer(str(sys.argv[1]),int(sys.argv[2])).start(int(sys.argv[3]))
    else:
        EchoServer(str(sys.argv[1]),int(sys.argv[2]),debug=True).start(int(sys.argv[3]))

