from mailbox import Mailbox
from random import randrange

class Connection:

    _max_seq = 1024

    _alpha = 1/8
    _beta = 1/4

    def __init__(self, addr, mb_len, mb_num):

        self._addr = addr
        self._mb_num = mb_num
        self._mb_len = mb_len
        self._mailboxes = [Mailbox(self._mb_len) for i in range(self._mb_num)]

        self._next_seq = randrange(Connection._max_seq)

        self._next_out_w_mailbox = 0
        self._next_out_r_mailbox = 0
        self._next_in_mailbox = 0

        self._estimated_rtt = 1
        self._rtt_dev = 1
        self._rto = 3000

        self.set_timeout(self._rto)

    def get_mailbox(self, i):

        return self._mailboxes[i]

    def send(self, message, mailbox=-1):

        if mailbox < 0 or mailbox >= self._mb_num:
    
            mailbox=-1
            for i in range(0,self._mb_num):
                index = (i+self._next_out_w_mailbox)  % self._mb_num
                
                if not self._mailboxes[index].get_output().is_full():
                    mailbox=index
                    break

            if mailbox == -1:
                return False

        self._next_out_w_mailbox = (mailbox+1) % self._mb_num

        message.set_global(self._next_seq)
        message.set_channel(mailbox)

        self._next_seq = (self._next_seq+1) % Connection._max_seq

        return self.get_mailbox(mailbox).send(message)


    def receive(self, mailbox = -1):

        if mailbox < 0 or mailbox >= self._mb_num:

            mailbox=-1
            for i in range(0,self._mb_num):
                index = (i+self._next_in_mailbox)  % self._mb_num
                if not self._mailboxes[index].get_input().is_empty():
                    mailbox=index
                    break

            if mailbox == -1:
                return None

        self._next_in_mailbox = (mailbox+1) % self._mb_num

        return self.get_mailbox(mailbox).receive()


    def next(self, mailbox=-1):

        if mailbox < 0 or mailbox >= self._mb_num:
        
            mailbox=-1
            for i in range(0,self._mb_num):
                index = (i+self._next_out_r_mailbox)  % self._mb_num
                if not self._mailboxes[index].get_output().is_empty():
                    mailbox=index
                    break

            if mailbox == -1:
                return None,None
    
        self._next_out_r_mailbox = (mailbox+1) % self._mb_num

        mailbox = self.get_mailbox(mailbox)

        return mailbox, mailbox.get_output().next()

    def set_timeout(self, delta):

        for m in self._mailboxes:
            m.set_timeout(delta)

    def calculate_rto(self, rtt):
        return 5000
        self._estimated_rtt = (1-Connection._alpha)*self._estimated_rtt + Connection._alpha*rtt
        self._rtt_dev = (1-Connection._beta)*self._rtt_dev + Connection._beta*abs(rtt-self._estimated_rtt)

        self._rto = self._estimated_rtt + 4*self._rtt_dev

        return self._rto

    def __repr__(self):
        return str(self._mailboxes)