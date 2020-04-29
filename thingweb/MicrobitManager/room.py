import requests
import time
import datetime
import json

class Room():

    def __init__(self, number):
        self.number = str(number)
        self.room = {
            "thing":{
                "title": "room"+self.number,
                "description": "A Smart Room",
                "descriptions": {
                    "it": "Una stanza intelligente"
                },
                "@context": "https://www.w3.org/2019/wot/td/v1",
                "properties": {
                    "last_indoor_update": {
                            "type": "string",
                            "description": "Last room's sensors update",
                            "descriptions": {
                                "it": "Ultimo aggiornamento dai sensori nella stanza"
                            },
                            "observable": True,
                            "readOnly": True
                        },
                        
                    "last_outdoor_update": {
                            "type": "string",
                            "description": "Last outdoor update",
                            "descriptions": {
                                "it": "Ultimo aggiornamento dei parametri esterni"
                            },
                            "observable": True,
                            "readOnly": True
                        }
                },
                "actions":{
                    "refresh": {
                        "description": "Update the parameters",
                        "descriptions": {
                            "it": "Aggiorna i parametri"
                        },
                        "output": { "type": "object" }
                    }
                },
                "events": {
                    "fix": {
                        "description": "Some action to do",
                        "descriptions": {
                            "it": "Qualche azione da compiere"
                        }
                    }
                }
            },
            "initialScript":'const fetch = require("node-fetch");const weatherapi = "http://api.weatherapi.com/v1/current.json?q=43,10&key=e5dec06056da4e81be1171342200504";const openweathermap = "http://api.openweathermap.org/data/2.5/weather?units=metric&lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c";const openweathermap_uvi = "http://api.openweathermap.org/data/2.5/uvi?lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c";',
            "endScript":"thing.writeProperty('temp', 0);thing.writeProperty('light', 0);thing.writeProperty('time', (new Date()).getHours());thing.writeProperty('outdoor_temp', 0);thing.writeProperty('outdoor_light', 0);thing.writeProperty('last_indoor_update', 0);thing.writeProperty('last_outdoor_update', 0);",
            "handlers":{
                "actions":{
                    "refresh":"thing.readAllProperties().then((map) => {resolve(map)})"
                },
                
                "properties":{
                    "time":{
                        "read":"resolve((new Date()).getHours())"
                    },
                    "outdoor_light":{
                        "read":'fetch(openweathermap_uvi).then((response) => {return response.json();}).then((data) => {thing.writeProperty("last_outdoor_update", (new Date()).toISOString());resolve((data["value"]/11)*255)});'
                    },
                    "outdoor_temp":{
                        "read":'fetch(openweathermap).then((response) => {return response.json();}).then((data) => {thing.writeProperty("last_outdoor_update", (new Date()).toISOString());resolve(data["main"]["feels_like"])});'
                    }

                }
            }
        }
        """
        self.add_param("temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"],"Room's temperature","Temperatura della stanza");
        self.add_param("light",[25,80], ["LOW","MEDIUM","HIGH"],"Room's light","Luminosita' della stanza");
        self.add_param("time",[7,13,19,22], ["NIGHT","MORNING","AFTERNOON","EVENING","NIGHT"],"Time","Orario");
    
        self.add_param("outdoor_light",[25,80], ["LOW","MEDIUM","HIGH"], "Outdoor light","Luminosita' esterna")
        self.add_param("outdoor_temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"], "Outdoor temperature","Temperatura esterna")
    """

        print(json.dumps(self.room))

    def add_param(self, name, thresholds, labels, description = "", descriptionIta = ""):
        self.room["thing"]["properties"][name] = {
            "type":"number",
            "description": description,
            "descriptions": {
                "it": descriptionIta
            },
            "observable": True,
            "readOnly": True,
            "#input": True
        }

        self.room["thing"]["properties"][name+"L"] = {
            "type":"string",
            "description": description+" in levels",
            "descriptions": {
                "it": descriptionIta+" in livelli"
            },
            "observable": True,
            "readOnly": True,
            "enum": list(set(labels)),
        }


        if(name not in self.room["handlers"]["properties"]):
            self.room["handlers"]["properties"][name] = {}
        
        self.room["handlers"]["properties"][name]["write"] = 'thing.writeProperty("'+name+"L"+'",value);thing.writeProperty("last_indoor_update", (new Date()).toISOString());resolve(value);'

        if(name+"L" not in self.room["handlers"]["properties"]):
            self.room["handlers"]["properties"][name+"L"] = {}
            
        nameL_handler = ""

        for i in range(len(thresholds)):
            nameL_handler += 'if(value < '+str(thresholds[i])+'){resolve("'+labels[i]+'");}'

        nameL_handler += 'resolve("'+labels[len(thresholds)]+'");'
        
        self.room["handlers"]["properties"][name+"L"]["write"] = nameL_handler

    def get_thing_description(self):
            return self.room
        
