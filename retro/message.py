
class Message:

    def __init__(self, _global, data = {}, mailbox = -1, seq = -1, ack = -1, syn = 0):

        self._data = data
        self._mailbox = mailbox
        self._seq = seq
        self._global = _global
        self._ack = ack
        self._from = []
        self._to = []
        self._syn = syn


    @staticmethod
    def make(dict):
        try:
            msg = Message(dict["global"],data=dict["data"],mailbox=dict["mailbox"],seq=dict["seq"],ack=dict["ack"],syn=dict["syn"])
            msg.set_sender((dict["from"][0],dict["from"][1]))
            msg.set_dest((dict["to"][0],dict["to"][1]))
            return msg  #normal msg
        except:
            try:
                msg = Message(-1,mailbox=dict["mailbox"],ack=dict["ack"])
                msg.set_sender((dict["from"][0],dict["from"][1]))
                msg.set_dest((dict["to"][0],dict["to"][1]))
                return msg #ack msg

            except: return None

    def get(self):

        return {
            "global": self._global, 
            "mailbox": self._mailbox, 
            "seq": self._seq, 
            "data": self._data, 
            "ack":self._ack,
            "syn":self._syn, 
            "from":self._from, 
            "to":self._to
            }

    def is_ack(self):

        return self._ack != -1

    def is_syn(self):

        return self._syn != 0

    def get_data(self):

        return self._data

    def get_sequence(self):
    
        return self._seq

    def get_global(self):
        
        return self._global

    def get_mailbox(self):
    
        return self._mailbox

    def get_ack(self):

        return self._ack

    def get_sender(self):

        return (self._from[0],self._from[1])

    def get_dest(self):
    
        return (self._to[0],self._to[1])

    def set_data(self, data):
    
        self._data = data
        
    def set_sequence(self, seq):
    
        self._seq = seq

    def set_global(self, g):
        
        self._global = g
          
    def set_mailbox(self, mailbox):
    
        self._mailbox = mailbox

    def set_dest(self, addr):
    
        self._to = [addr[0], addr[1]]
    
    def set_sender(self, addr):

        self._from = [addr[0], addr[1]]

    def set_syn(self):

        self._syn = 1

    def __repr__(self):
        return str(self.get())
