import math

class Microbit():

    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.friendly_name = Microbit.get_microbit_name(serial_number)

        self.td = {
            "thing":{
                "title": self.friendly_name,
                "description": "A Microbit Device",
                "descriptions": {
                    "it": "Un Microbit"
                },
                "@context": "https://www.w3.org/2019/wot/td/v1",
                "properties": {
                    "serial_number": {
                        "type": "float",
                        "description": "This Microbit's serial number",
                        "descriptions": {
                            "it": "Numero seriale del Microbit"
                        },
                        "observable": False,
                        "readOnly": True
                    },
                    "light": {
                            "type": "number",
                            "description": "Value of this Microbit's light sensor",
                            "descriptions": {
                                "it": "Valore del sensore di luminosita' di questo Microbit"
                            },
                            "observable": True,
                            "#input":True
                            },
                    "temp": {
                            "type": "number",
                            "description": "Value of this Microbit's temp sensor",
                            "descriptions": {
                                "it": "Valore del sensore di temperatura di questo Microbit"
                            },
                            "observable": True,
                            "#input":True
                        }
                    },
                    "actions":{
                        "set_temperature": {
                            "description": "Request a new temperature settings",
                            "descriptions": {
                                "it": "Richiedi nuova impostazione della temperatura"
                            },
                            "input": { "type": "object" },
                            "output": { "type": "object" }
                        },
                        "set_light": {
                                "description": "Request a new light settings",
                                "descriptions": {
                                    "it": "Richiedi nuova impostazione della luce"
                                },
                                "input": { "type": "object" },
                                "output": { "type": "object" }
                            }
                        }
                },
                "initialScript":'thing.writeProperty("serial_number", '+str(serial_number)+');thing.writeProperty("temp", 0);thing.writeProperty("light", 0);',
                "handlers":{
                    "actions":{
                        "set_temperature":"console.debug('TEMPERATURE: '+JSON.stringify(input));",
                        "set_light":"console.debug('LIGHT: '+JSON.stringify(input));",
                    },
                }
            }

    def get_thing_description(self):
        return self.td

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