from random import randrange
import socket
import time
import json
import threading
from itertools import cycle
from message import Message
from connection import Connection
from mailbox import Mailbox
from channel import Channel

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
        
        self._cmd_callback = lambda msg: ()
        self._send_callback = lambda msg: ()
        self._rcv_callback = lambda msg: ()

        self._cmd_queue = []

        self._socket_lock = threading.RLock()
        self._conn_lock = threading.RLock()
        self._cmd_lock = threading.RLock()


    def _put_cmd(self, msg):

        self._cmd_lock.acquire()

        self._cmd_queue.append(msg)

        self._cmd_lock.release()

    def get_cmd(self):
    
        self._cmd_lock.acquire()

        cmd = None
        try:
            cmd = self._cmd_queue.pop(0)
        except:
            pass

        self._cmd_lock.release()

        return cmd


    def get_connection(self, addr):

        self._conn_lock.acquire()

        if addr not in self._connections:

            self._connections[addr] = Connection(addr, self._mb_len, self._mb_num)
            self._conn_iterator = cycle(self._connections)

        data = self._connections[addr]

        self._conn_lock.release()

        return data

    def remove_connection(self, addr):

        self._conn_lock.acquire()

        if addr in self._connections:
            del self._connections[addr]
            self._conn_iterator = cycle(self._connections)

        self._conn_lock.release()


    def get_connections_size(self):
    
        self._conn_lock.acquire()

        size = len(self._connections)

        self._conn_lock.release()

        return size

    def get_connections_copy(self):
        
        self._conn_lock.acquire()

        copy = self._connections.copy()

        self._conn_lock.release()

        return copy


    def send(self, message, dest, mailbox = None):

        message = Message(-1, data = message)
        message.set_dest(dest)
        message.set_sender(self._addr)

        if mailbox is not None and mailbox < 0:
            message.set_mailbox(mailbox)
            return self._sock_send(message, dest)
            

        return self.get_connection(dest).send(message,mailbox)


    def receive(self, addr=None, mailbox = None):

        if addr is None:

            for i in range(self.get_connections_size()):
                c = self.get_connection(next(self._conn_iterator))
                msg =  c.receive(mailbox)

                if msg is not None:
                    return msg

                if c.is_close():
                    self.remove_connection(c.get_addr())

            return None
        
        return self.get_connection(addr).receive(mailbox)
        

    def start(self):

        threading.Thread(daemon=True, target=self._socket_receiver).start()
        threading.Thread(daemon=True, target=self._socket_sender).start()

    def _socket_receiver(self):
        
        while not self._shutdown:

            msg = self._sock_receive()
                
            if msg is not None:

                conn =  self.get_connection(msg.get_sender())

                if msg.get_mailbox() < 0:
                    self._cmd_callback(msg)

                    if msg.get_mailbox() == -1:
                        self.send({"len":self._mb_len,"num":self._mb_num},msg.get_sender(),mailbox=-2)
                    else:
                        self._put_cmd(msg)
                else:

                    mailbox = conn.get_mailbox(msg.get_mailbox())

                    if msg.is_ack():
                        
                        if not mailbox.get_output().is_empty() and mailbox.get_output().next().get_sequence() == msg.get_ack():
                            
                            mailbox.ack(msg.get_ack())
                            mailbox.get_output().get()
                            conn.calculate_rto(mailbox.stop_timer())
                    else:
                        self._rcv_callback(msg)
                        mailbox.post(msg)
                        message = Message(-1,mailbox=msg.get_mailbox(),ack=msg.get_sequence())
                        message.set_sender(self._addr)
                        message.set_dest(msg.get_sender())
                        self._sock_send(message,msg.get_sender())

                conn.standby()

        self._sock.close()


    def _socket_sender(self):

        while not self._shutdown:
            
            for a,c in self.get_connections_copy().items():
            
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

    def command_callback(self, func):
        self._cmd_callback = func

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
            try:
                self._socket_lock.release()
            except:
                pass
            return None

    def __repr__(self):
        return str(self._connections)


if __name__ == "__main__":   
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
    s2.command_callback(lambda message:print("command",message))
    s2.send_callback(lambda message:print("send",message))
    s1.receive_callback(lambda message:print("receive",message))
    while True:
        time.sleep(1)
        s2.send(i,("127.0.0.1",p1),mailbox=-1)
        #s3.send(i,("127.0.0.1",p1))
        i=i+1
        msg = s1.receive()
        #print("recived command:",s2.get_cmd())
        """while msg is None:
            msg = s1.receive()
        print(msg)"""
