
class Message:

    def __init__(self, _global, data = {}, channel = -1, seq = -1, ack = -1):

        self._data = data
        self._channel = channel
        self._seq = seq
        self._global = _global
        self._ack = ack
        self._from = []
        self._to = []


    @staticmethod
    def make(dict):
        try:
            msg = Message(dict["global"],data=dict["data"],channel=dict["channel"],seq=dict["seq"],ack=dict["ack"])
            msg.set_sender((dict["from"][0],dict["from"][1]))
            msg.set_dest((dict["to"][0],dict["to"][1]))
            return msg  #normal msg
        except:
            try:
                msg = Message(-1,channel=dict["channel"],ack=dict["ack"])
                msg.set_sender((dict["from"][0],dict["from"][1]))
                msg.set_dest((dict["to"][0],dict["to"][1]))
                return msg #ack msg

            except: return None

    def get(self):

        return {"global": self._global, "channel": self._channel, "seq": self._seq, "data": self._data, "ack":self._ack, "from":self._from, "to":self._to}

    def is_ack(self):
        return self._ack != -1

    def get_data(self):

        return self._data

    def get_sequence(self):
    
        return self._seq

    def get_global(self):
        
        return self._global

    def get_channel(self):
    
        return self._channel

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
          
    def set_channel(self, channel):
    
        self._channel = channel

    def set_dest(self, addr):
    
        self._to = [addr[0], addr[1]]
    
    def set_sender(self, addr):

        self._from = [addr[0], addr[1]]

    def __repr__(self):
        return str(self.get())
