from thing import Thing
from action import Action
from event import Event
from property import Property
from value import Value
from timer import Timer
import requests
import time
import datetime
import json
import configparser

# WEATHER API (10.000 calls/month)
# MORE INFO per Call
# FEEL LIKE TEMP WRONG?
def call_weatherapi():
    try:
        API_KEY = "e5dec06056da4e81be1171342200504"
        api_call = "http://api.weatherapi.com/v1/current.json?q="+LAT+","+LON+"&key="+API_KEY
        report = requests.get(api_call)
        if report.status_code == requests.codes.ok:
            report = report.json()
            temp = report["current"]["temp_c"]
            light = (float(report["current"]["uv"])/11)*255 # uv index max 11
            return True,temp,light
    except:
        pass
    return False,None,None

# OPEN WEATHER MAP (60 calls/min) (30 because two calls for request: weather and uv)
# or 1.000/day with one call api
# MORE PRECISE
def call_openweathermap():
    try:
        API_KEY = "647aa595e78b34e517dad92e1cf5e65c"
        api_call_temp = "http://api.openweathermap.org/data/2.5/weather?units=metric&lat="+LAT+"&lon="+LON+"&appid="+API_KEY
        api_call_uvi = "http://api.openweathermap.org/data/2.5/uvi?lat="+LAT+"&lon="+LON+"&appid="+API_KEY
        report_temp = requests.get(api_call_temp)
        report_uvi = requests.get(api_call_uvi)
        if report_temp.status_code == requests.codes.ok or report_uvi.status_code == requests.codes.ok:
            temp = None
            light = None
            if report_temp.status_code == requests.codes.ok:
                report_temp = report_temp.json()
                temp = report_temp["main"]["temp"]
            if report_uvi.status_code == requests.codes.ok:
                report_uvi = report_uvi.json()
                light = (float(report_uvi["value"])/11)*255 # uv index max 11
            return True,temp,light
    except:
        pass

    return False,None,None

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

        self.add_available_event(
                "fix",
                {
                    'description': ""
                })

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
            self.update_params()
            self.update(("last_outdoor_update"),str(datetime.datetime.now()))

        value = label[len(threshold)]

        for i in range(len(threshold)):
            if val < threshold[i]:
                value = label[i]
                break
        
        old = self.get_property(name+"L")
        if value != old:
            self.update((name+"L"),value)
            self.add_new_event(value+"_"+name, val)
            self.change(name,old,value)

    def change(self, name, old, new):

        config = configparser.ConfigParser()
        config.read('../../config.ini')

        test = config["TEST"].getboolean("TEST")

        if test:
            MY_IP = config["TEST"]["MY_IP"]
        else:
            MY_IP = config["DEFAULT"]["MY_IP"]

        MEDIATOR_PORT = config["MEDIATOR"]["PORT"]

        try:
            mediator = "http://"+MY_IP+":"+str(MEDIATOR_PORT)+"/"
            r = requests.get(mediator, json=self.get_properties())
            text = r.text
            self.add_new_event("fix", text)
        except:
            pass

    def update_params(self):

        config = configparser.ConfigParser()
        config.read('../../config.ini')

        global LAT
        global LON

        LAT = config["PLACE"]["LAT"]
        LON = config["PLACE"]["LON"]

        now = datetime.datetime.now()
        self.update("time",now.hour)
        
        light_backup = None
        temp_backup = None
        status_backup = False

        status,temp,light = call_openweathermap()

        if not status or temp is None or light is None:

            status_backup,temp_backup,light_backup = call_weatherapi()
        
        if status or status_backup:

            if light is not None:
                self.update("outdoor_light",light)
            elif light_backup is not None:
                self.update("outdoor_light",light_backup)

            if temp is not None:
                self.update("outdoor_temp",temp)
            elif temp_backup is not None:
                self.update("outdoor_light",temp_backup)

            self.update(("last_outdoor_update"),str(now))