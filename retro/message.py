from header import header
import sys

class Message:

    def __init__(self, _global, data = b'\x00', mailbox = -1, seq = -1, ack = 0, syn = 0):

        self.set_data(data)
        self.set_mailbox(mailbox)
        self.set_sequence(seq)
        self.set_global(_global)

        if ack != 0:
            self.set_ack()
        else:
            self._ack = 0

        if syn != 0:
            self.set_syn()
        else:
            self._syn = 0

        self._from = None
        self._to = None

    @staticmethod
    def make_from_json(dict):
        try:
            msg = Message(dict["global"],data=dict["data"],mailbox=dict["mailbox"],seq=dict["seq"],ack=dict["ack"],syn=dict["syn"])
            return msg  #normal msg
        except:
            try:
                msg = Message(-1,mailbox=dict["mailbox"],ack=dict["ack"],seq=dict["seq"])
                return msg #ack msg

            except:
                return None

    @staticmethod
    def make(b):
        size = 0
        g = int.from_bytes((b[size:size+header["global"]]), byteorder='big', signed=True)
        size = size + header["global"]
        m = int.from_bytes((b[size:size+header["mailbox"]]), byteorder='big', signed=True)
        size = size + header["mailbox"]
        s = int.from_bytes((b[size:size+header["sequence"]]), byteorder='big', signed=True)
        size = size + header["sequence"]
        a = int.from_bytes((b[size:size+1]), byteorder='big')
        size = size + 1
        sy = int.from_bytes((b[size:size+1]), byteorder='big')
        size = size + 1
        data = b[size:]

        return Message(_global=g,mailbox=m,seq=s,ack=a,syn=sy,data=data)


    def get(self):
        
        return self.get_global().to_bytes(header["global"],"big", signed=True) + self.get_mailbox().to_bytes(header["mailbox"],"big", signed=True) + self.get_seq_num().to_bytes(header["sequence"],"big", signed=True) + self.is_ack().to_bytes(1,"big") + self.is_syn().to_bytes(1,"big") + self.get_data()
            

    def json(self):
    
        return {
            "global": self.get_global(), 
            "mailbox": self.get_mailbox(), 
            "seq": self.get_seq_num(), 
            "data": self.get_data(), 
            "ack":self.is_ack(),
            "syn":self.is_syn(), 
            }

    def is_ack(self):

        return self._ack

    def is_syn(self):

        return self._syn

    def get_data(self):
        
        return self._data

    def get_seq_num(self):

        return self._seq

    def get_sequence(self):
    
        if self.is_ack() == 0:
            return self._seq
        else:
            return -1

    def get_global(self):
        
        return self._global

    def get_mailbox(self):
    
        return self._mailbox

    def get_ack(self):

        if self.is_ack():
            return self._seq
        else:
            return -1

    def get_sender(self):

        return self._from

    def get_dest(self):
    
        return self._to

    def set_data(self, data):
    
        self._data = data
        
    def set_sequence(self, seq):
        
        self._seq = seq

    def set_global(self, g):
        
        self._global = g
          
    def set_mailbox(self, mailbox):
    
        self._mailbox = mailbox

    def set_dest(self, addr):
    
        self._to = addr
    
    def set_sender(self, addr):

        self._from = addr

    def set_syn(self):

        self._syn = 1

    def set_ack(self):
    
        self._ack = 1

    def __repr__(self):
        return str(self.get())


