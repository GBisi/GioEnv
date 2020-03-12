from channel import Channel
from mailbox import Mailbox
from message import Message
from connection import Connection
from random import randrange
import socket
import time
import json
import threading
from itertools import cycle

class MySocket:

    _max_mb = 16
    _max_msg_size = 2048

    def __init__(self, port, mb_len = 1, mb_num = 1, ip = "127.0.0.1", debug = False):

        self._mb_num = min(mb_num,MySocket._max_mb)
        self._mb_len = mb_len
        self._connections = {}

        self._conn_iterator = cycle(self._connections)

        self._shutdown = False

        self._addr = (ip, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(self._addr)
        self._sock.setblocking(False)
        self._debug = debug
        
        self._err_callback = lambda msg: ()
        self._send_callback = lambda msg: ()
        self._rcv_callback = lambda msg: ()

        self._socket_lock = threading.RLock()


    def get_connection(self, addr):

        if addr not in self._connections:

            self._connections[addr] = Connection(addr, self._mb_len, self._mb_num)
            self._conn_iterator = cycle(self._connections)

        return self._connections[addr]


    def send(self, message, dest, mailbox = -1):

        message = Message(-1, data = message)
        message.set_dest(dest)
        message.set_sender(self._addr)

        if mailbox < -1:
            return self._sock_send(message, dest)
            

        return self.get_connection(dest).send(message,mailbox)


    def receive(self, addr=None, mailbox = -1):

        if addr is None:

            for i in range(len(self._connections)):
                c = self._connections[next(self._conn_iterator)]
                msg =  c.receive(mailbox)
                if msg is not None:
                    return msg
            return None
        
        return self.get_connection(addr).receive(mailbox)
        

    def start(self):

        threading.Thread(target=self._socket_receiver).start()
        threading.Thread(target=self._socket_sender).start()

    def _socket_receiver(self):
        
        while not self._shutdown:

            msg = self._sock_receive()
                
            if msg is not None:

                if msg.get_channel() < 0:

                    self._err_callback(msg)

                else:
                
                    self._rcv_callback(msg)

                    conn =  self.get_connection(msg.get_sender())

                    mailbox = conn.get_mailbox(msg.get_channel())

                    if msg.is_ack():
                        
                        if not mailbox.get_output().is_empty() and mailbox.get_output().next().get_sequence() == msg.get_ack():
                            
                            mailbox.get_output().get()
                            conn.calculate_rto(mailbox.stop_timer())
                    else:
                        mailbox.post(msg)
                        message = Message(-1,channel=msg.get_channel(),ack=msg.get_sequence())
                        message.set_sender(self._addr)
                        message.set_dest(msg.get_sender())
                        self._sock_send(message,msg.get_sender())

        self._sock.close()


    def _socket_sender(self):

        while not self._shutdown:
            
            for a,c in self._connections.items():
            
                mailbox,message = c.next()
                
                if message is not None and mailbox.timeout():

                    mailbox.start_timer()
                    if self._sock_send(message, message.get_dest()):
                        self._send_callback(message)

        self._sock.close()

    def _task(self, f):
        threading.Thread(target=f).start()

    def shutdown(self):
        self._shutdown = True

    def error_callback(self, func):
        self._err_callback = func

    def send_callback(self, func):
        self._send_callback = func

    def receive_callback(self, func):
        self._rcv_callback = func


    def _sock_send(self, message, dest):

        try:
            message = str(message).encode("utf-8")
            self._socket_lock.acquire()
            self._sock.sendto(message, dest)
            self._socket_lock.release()
            if self._debug:
                print(self._addr,"send:",message)
            return True
        except:
            self._socket_lock.release()
            return False

    def _sock_receive(self):
        try:
            self._socket_lock.acquire()
            msg = self._sock.recv(MySocket._max_msg_size)
            self._socket_lock.release()
            msg = json.loads(msg.decode("utf-8").replace("\'", "\""))
            if self._debug:
                print(self._addr,"receive:",msg)
            msg = Message.make(msg)
            if self._addr != msg.get_dest():
                return None

            return msg
        except:
            self._socket_lock.release()
            return None

    def __repr__(self):
        return str(self._connections)

       
p1 = 4242
p2 = 4343
p3 = 4444
s1 = MySocket(p1,3,64,debug=False)
#s1.send(1,("127.0.0.1",p2))
s1.start()
s2 = MySocket(p2,3,3)
#s2.send(1,("127.0.0.1",p1))
s2.start()
"""while s1.receive() is None:
    pass
s3 = MySocket(p3,3,3)
s3.send(1,("127.0.0.1",p1))
s3.send(1,("127.0.0.1",p2))
s3.send(2,("127.0.0.1",p1))
s3.start()"""
i = 0
s2.error_callback(lambda message:print("error",message))
s2.send_callback(lambda message:print("send",message))
s2.receive_callback(lambda message:print("receive",message))
while True:
    s2.send(i,("127.0.0.1",p1))
    #s3.send(i,("127.0.0.1",p1))
    i=i+1
    msg = s1.receive()
    """while msg is None:
        msg = s1.receive()
    print(msg)"""
