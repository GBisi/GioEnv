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
                            'light',
                            Value(0, lambda v: self.set_light_level(v)),
                            metadata={
                                'title': 'Light',
                                'type': 'number',
                            }))

        self.add_property(
                    Property(self,
                            'temp',
                            Value(0, lambda v: self.set_temp_level(v)),
                            metadata={
                                'title': 'temperature',
                                'type': 'number',
                            }))

        self.add_property(
                    Property(self,
                            'lightL',
                            Value("LOW"),
                            metadata={
                                'title': 'light level',
                                'type': 'string',
                            }))

        self.add_property(
                    Property(self,
                            'tempL',
                            Value("LOW"),
                            metadata={
                                'title': 'temperature level',
                                'type': 'string',
                            }))

    def get_number(self):
        return self.number

    def update(self, name, value):
        self.set_property(name, value)

    def set_light_level(self, value):
        if value > 80:
            value = "HIGH"
        elif value < 20:
            value = "LOW"
        else:
            value = "OPTIMAL" 
        self.update("lightL",value)

    def set_temp_level(self, value):
        if value > 22:
            value = "HIGH"
        elif value < 18:
            value = "LOW"
        else: 
            value = "OPTIMAL" 
        self.update("tempL",value)