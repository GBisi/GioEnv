from thing import Thing
from action import Action
from event import Event
from property import Property
from value import Value
from timer import Timer

class Room(Thing):

    def __init__(self, number):
        self.number = str(number)

        Thing.__init__(
                    self,
                    "room"+self.number,
                    'Room Id: '+self.number,
                    'A Room'
                )

        self.add_param("light",[25,80], ["LOW","MEDIUM","HIGH"])
        self.add_param("temp",[18,20,22,24], ["FREEZING","COLD","MEDIUM","WARM","HOT"])

    def add_param(self, name, threshold, label):

        self.add_property(
                    Property(self,
                            name,
                            Value(0, lambda v: self.set_param(name, v, threshold, label)),
                            metadata={
                                'title': name,
                                'type': 'number',
                                'readOnly': True,
                            }))

        self.add_property(
                    Property(self,
                            name+'L',
                            Value(label[0]),
                            metadata={
                                'title': name+' level',
                                'type': 'string',
                                'readOnly': True,
                                'enum':label,
                            }))

        for l in label:
            self.add_available_event(
                l+'_'+name,
                {
                    'description': ""
                })



    def get_number(self):
        return self.number

    def set_param(self, name, val, threshold, label):
        value = label[len(threshold)]

        for i in range(len(threshold)):
            if val < threshold[i]:
                value = label[i]
                break
        
        
        if value != self.get_property(name+"L"):
            self.update((name+"L"),value)
            self.add_new_event(value+"_"+name, val)