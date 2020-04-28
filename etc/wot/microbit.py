from thing import Thing
from action import Action
from event import Event
from property import Property
from value import Value
from timer import Timer
import math

class Microbit(Thing):

    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.friendly_name = Microbit.get_microbit_name(serial_number)

        Thing.__init__(
                    self,
                    self.friendly_name,
                    'Microbit: '+self.friendly_name,
                    'A Microbit Devices'
                )

        self.add_property(
                    Property(self,
                            'light',
                            Value(0),
                            metadata={
                                'title': 'Light',
                                'type': 'number',
                                'readOnly': True,
                            }))

        self.add_property(
                    Property(self,
                            'temp',
                            Value(0),
                            metadata={
                                'title': 'temperature',
                                'type': 'number',
                                'readOnly': True,
                            }))

    def get_serial_number(self):
        return self.serial_number

    def get_friendly_name(self):
        return self.friendly_name

    #https://github.com/lancaster-university/microbit-dal/blob/master/source/core/MicroBitDevice.cpp
    @staticmethod
    def get_microbit_name(serial_number):
        n = math.ceil(serial_number)
        name_len = 5
        code_letters = 5
        codebook = [
            ['z', 'v', 'g', 'p', 't'],
            ['u', 'o', 'i', 'e', 'a'],
            ['z', 'v', 'g', 'p', 't'],
            ['u', 'o', 'i', 'e', 'a'],
            ['z', 'v', 'g', 'p', 't']
        ]

        ld = 1
        d = code_letters
        name = ""

        for i in range(name_len):
            h = int((n % d) / ld);
            n -= h;
            d *= code_letters;
            ld *= code_letters;
            name = codebook[i][h] + name

        return name
"""
print(Microbit.get_microbit_name(384933164)) #puvit
print(Microbit.get_microbit_name(1252840479.9999999)) #tetoz
print(Microbit.get_microbit_name(671265031)) #tuvov
print(Microbit.get_microbit_name(20458004765.9999998)) #gezev
"""