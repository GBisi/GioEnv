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

        self.add_property(
                    Property(self,
                            'temp',
                            Value(0, lambda v: self.set_temp_level(v)),
                            metadata={
                                'title': 'temperature',
                                'type': 'number',
                                'readOnly': True,
                            }))

        self.add_property(
                    Property(self,
                            'tempL',
                            Value("LOW"),
                            metadata={
                                'title': 'temperature level',
                                'type': 'string',
                                'readOnly': True,
                            }))


        

    def add_param(self, name, min_, max_):
        self.add_property(
                    Property(self,
                            name,
                            Value(0, lambda v: self.set_param(name, v, min_, max_)),
                            metadata={
                                'title': name,
                                'type': 'number',
                                'readOnly': True,
                            }))

        self.add_property(
                    Property(self,
                            name+'L',
                            Value("LOW"),
                            metadata={
                                'title': name+' level',
                                'type': 'string',
                                'readOnly': True,
                            }))

        self.add_available_event(
            'high_'+name,
            {
                'description': ""
            })

        self.add_available_event(
            'low_'+name,
            {
                'description': ""
            })


    def get_number(self):
        return self.number

    def set_param(self, name, value, min_, max_):
        if value > max_:
            value = "HIGH"
        elif value < min_:
            value = "LOW"
        else:
            value = "MEDIUM" 
        self.update(name+"L",value)