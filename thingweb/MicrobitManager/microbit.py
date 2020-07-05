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
                    "dashboard": {
                        "type": "string",
                        "description": "This Microbit's dashboard url",
                        "descriptions": {
                            "it": "Url della dashboard di questo microbit"
                        },
                        "observable": False,
                        "readOnly": True
                    },
                    "serial_number": {
                        "type": "float",
                        "description": "This Microbit's serial number",
                        "descriptions": {
                            "it": "Numero seriale del Microbit"
                        },
                        "observable": False,
                        "readOnly": True
                    },
                    "rooms": {
                        "type": "object",
                        "description": "Rooms controlled by this microbit",
                        "descriptions": {
                            "it": "Stanze controllate da questo microbit"
                        },
                        "observable": True,
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
                    "temperature": {
                            "type": "number",
                            "description": "Value of this Microbit's temperature sensor",
                            "descriptions": {
                                "it": "Valore del sensore di temperatura di questo Microbit"
                            },
                            "observable": True,
                            "#input":True
                        }
                    },
                    "actions": {
                        "set": {
                            "description": "Set a parameter",
                            "descriptions": {
                                "it": "Imposta un parametro"
                            },
                            "input": {
                                "type": 'object',
                            },
                        }
                    },
                    "events": {
                        "setup_temperature": {
                            "description": "A new setup of the temp enviroment",
                            "descriptions": {
                                "it": "Un nuovo setup della temperatura dell'ambiente"
                            },
                            "data": {
                                "type": 'object',
                            },
                        },
                        "setup_light": {
                            "description": "A new setup of the light enviroment",
                            "descriptions": {
                                "it": "Un nuovo setup della luminosità dell'ambiente"
                            },
                            "data": {
                                "type": 'object',
                            },
                        } 
                    },
                },
                "initialScript":'thing.writeProperty("dashboard","http://131.114.73.148:2042/dash/'+self.friendly_name+'");thing.writeProperty("rooms",{});thing.writeProperty("serial_number", '+str(serial_number)+');thing.writeProperty("temperature", 0);thing.writeProperty("light", 0);',
                 "handlers":{
                    "actions":{
                        "set":"console.debug('Set:');console.debug(input);setup={}; if(input['param']=='temperature'){setup['temperature']=input['val']} if(input['param']=='light'){setup['light']=input['val']} console.debug('Event:'); console.debug(setup); thing.emitEvent('setup_'+input['param'],setup);",
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

if __name__ == "__main__":

    print(Microbit.get_microbit_name(384933164)) #puvit
    print(Microbit.get_microbit_name(1252840479.9999999)) #tetoz
    print(Microbit.get_microbit_name(671265031)) #tuvov
    print(Microbit.get_microbit_name(20458004765.9999998)) #gezev
