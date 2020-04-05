from thing import Thing
from action import Action
from event import Event
from property import Property
from value import Value
from timer import Timer
import requests
import time
import datetime

LAT = "43.720664"
LON = "10.408427"

# OPEN WEATHER MAP
API_KEY = "647aa595e78b34e517dad92e1cf5e65c"
api_call = "http://api.openweathermap.org/data/2.5/weather?lat="+LAT+"&lon="+LON+"&appid="+API_KEY+"?"

# WEATHER API
API_KEY = "e5dec06056da4e81be1171342200504"
api_call = "http://api.weatherapi.com/v1/current.json?q="+LAT+","+LON+"&key="+API_KEY

class Room(Thing):

    def __init__(self, number):
        self.number = str(number)

        Thing.__init__(
                    self,
                    "room"+self.number,
                    'Room Id: '+self.number,
                    'A Room'
                )

        self.add_param("time",[7,13,19,22], ["NIGHT","MORNING","AFTERNOON","EVENING","NIGHT"])

        self.add_param("light",[25,80], ["LOW","MEDIUM","HIGH"])
        self.add_param("temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"])

        self.add_param("outdoor_light",[25,80], ["LOW","MEDIUM","HIGH"])
        self.add_param("outdoor_temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"])

        self.add_property(
                    Property(self,
                            "last_indoor_update",
                            Value(0),
                            metadata={
                                'title':"last_indoor_update",
                                'type': 'number',
                                'readOnly': True,
                            }))

        self.add_property(
                    Property(self,
                            "last_outdoor_update",
                            Value(0),
                            metadata={
                                'title': "last_outdoor_update",
                                'type': 'number',
                                'readOnly': True,
                            }))

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

        if name == "temp" or name == "light":
            self.update(("last_outdoor_update"),str(datetime.datetime.now()))

        value = label[len(threshold)]

        for i in range(len(threshold)):
            if val < threshold[i]:
                value = label[i]
                break
        
        
        if value != self.get_property(name+"L"):
            self.update((name+"L"),value)
            self.add_new_event(value+"_"+name, val)

    def update_params(self):

        report = requests.get(api_call)
        now = datetime.datetime.now()
        self.update("time",now.hour)


        if report.status_code == requests.codes.ok:
            report = report.json()
            temp = report["current"]["feelslike_c"]
            light = (float(report["current"]["vis_km"])/10)*255 #visibility max 10 km

            self.update("outdoor_light",light)
            self.update("outdoor_temp",temp)

            self.update(("last_outdoor_update"),str(now))