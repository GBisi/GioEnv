import requests
import time
import datetime
import json

class Room():

    def __init__(self, number, temperature_microbit, light_microbit):
        self.number = str(number)
        self.temperature_microbit = "http://131.114.73.148:2000/"+temperature_microbit
        self.light_microbit = "http://131.114.73.148:2000/"+light_microbit
        self.room = {
            "thing":{
                "title": "room"+self.number,
                "description": "A Smart Room",
                "descriptions": {
                    "it": "Una stanza intelligente"
                },
                "@context": "https://www.w3.org/2019/wot/td/v1",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "This Room's dashboard url",
                        "descriptions": {
                            "it": "Url della dashboard di questa stanza"
                        },
                        "observable": False,
                        "readOnly": True
                    },
                    "temperature_microbit":{
                        "type": "string",
                        "description": "Temperature microbit url",
                        "descriptions": {
                            "it": "Url del microbit che si occupa della temperatura"
                        },
                        "observable": False,
                        "readOnly": True
                    },
                    "light_microbit":{
                        "type": "string",
                        "description": "Light microbit url",
                        "descriptions": {
                            "it": "Url del microbit che si occupa della luminosità"
                        },
                        "observable": False,
                        "readOnly": True
                    },
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
                        },

                    "users": {
                        "type":"array",
                        "description": "Users in the room",
                            "descriptions": {
                                "it": "Utenti nella stanza"
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
                    },
                    "mediate": {
                        "description": "Mediate users preferences",
                        "descriptions": {
                            "it": "Media tra le preferenze degli utenti"
                        },
                        "output": { "type": "object" }
                    },
                     "enter": {
                        "description": "Enter in the room",
                        "descriptions": {
                            "it": "Entra nella stanze"
                        },
                        "input": { "type": "string" }
                    },
                    "leave": {
                        "description": "Leave the room",
                        "descriptions": {
                            "it": "Esci dalla stanze"
                        },
                        "input": { "type": "string" }
                    },
                },
            },
            "initialScript":'function sleep (time) {return new Promise((resolve) => setTimeout(resolve, time));};const eaas = "http://131.114.73.148:1999/";const s2m = "http://131.114.73.148:2048/";const fetch = require("node-fetch");const weatherapi = "https://api.weatherapi.com/v1/current.json?q=43,10&key=e5dec06056da4e81be1171342200504";const openweathermap = "https://api.openweathermap.org/data/2.5/weather?units=metric&lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c";const openweathermap_uvi = "https://api.openweathermap.org/data/2.5/uvi?lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c";function listtojson(ls){obj={};if(ls != "[]" && ls !=""){ls = ls.replace("[","").replace("]","").split(", ");for(let elem in ls){elem=ls[elem].split("(");name = elem[0];value=elem[1];obj[name]=value.replace(")","")}}return obj};function jsontolist(obj){ls = [];for(key in obj){val = obj[key];if(typeof val === "object"){val = jsontolist(val)}ls.push(key +"("+val+")")}return ls};thing.writeProperty("dashboard","http://131.114.73.148:2042/dash/room'+self.number+'");',
            "endScript":"thing.writeProperty('temperature_microbit','"+self.temperature_microbit+"');thing.writeProperty('light_microbit','"+self.light_microbit+"'); thing.writeProperty('users', []);thing.writeProperty('temperature', 0);thing.writeProperty('light', 0);thing.writeProperty('time', (new Date()).getHours());thing.writeProperty('outdoor_temperature', 0);thing.writeProperty('outdoor_light', 0);thing.writeProperty('last_indoor_update', 0);thing.writeProperty('last_outdoor_update', 0);",
            "handlers":{
                "actions":{
                    "refresh":"thing.readAllProperties().then((map) => {resolve(map)})",
                    "enter":"thing.readProperty('users').then((users) => { if (!(users.includes(input))) { users.push(input); resolve('User registered'); thing.invokeAction('mediate'); } else { resolve('User already in the room'); }; });",
                    "leave":"thing.readProperty('users').then((users) => { if (!(users.includes(input))) { resolve('User not in the room'); } else { const index = users.indexOf(input); users.splice(index, 1); resolve('User removed'); thing.invokeAction('mediate'); }; });",
                    "mediate":"data = []; thing.readAllProperties().then((props) => {data.push('users_num(' + props['users'].length + ',"+self.number.lower()+").'); data.push('time(' + props['timeL'].toLowerCase() + ', "+self.number.lower()+").'); data.push('light(' + props['lightL'].toLowerCase() + ', "+self.number.lower()+").'); data.push('outdoor_light(' + props['outdoor_lightL'].toLowerCase() + ', "+self.number.lower()+").'); data.push('temperature(' + props['temperatureL'].toLowerCase() + ', "+self.number.lower()+").'); data.push('outdoor_temperature(' + props['outdoor_temperatureL'].toLowerCase() + ', "+self.number.lower()+").'); data.push('room(' + "+self.number.lower()+" + ').'); data.push('actuator("+self.temperature_microbit.split("/")[-1].lower()+",temperature, "+self.number.lower()+").'); data.push('actuator("+self.light_microbit.split("/")[-1].lower()+",light, "+self.number.lower()+").'); for (const u in props['users']) { data.push('user('+props['users'][u].toLowerCase()+').'); data.push('inRoom(' + props['users'][u].toLowerCase() + ',"+self.number.lower()+").'); }; console.debug(data); resolve(data); fetch('http://131.114.73.148:2000/mediator/actions/mediate', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'room':{ 'number': '"+self.number.lower()+"', 'facts': data, 'users':props['users'] } }) }) });"
                    }, 
                "properties":{
                    "time":{
                        "read":"resolve((new Date()).getHours())"
                    },
                    "outdoor_light":{
                        "read":'fetch(openweathermap_uvi).then((response) => {return response.json();}).then((data) => {thing.writeProperty("last_outdoor_update", (new Date()).toISOString());if(data["value"]==null){throw "Error"};resolve(((data["value"])/11)*255);}).catch((e)=>{console.debug("LIGHT API ERROR"); resolve(thing.properties["outdoor_light"].getState().value); });'
                    },
                    "outdoor_temperature":{
                        "read":'fetch(openweathermap).then((response) => {return response.json();}).then((data) => {thing.writeProperty("last_outdoor_update", (new Date()).toISOString());resolve(data["main"]["feels_like"]);}).catch((e)=>{console.debug("TEMPERATURE API ERROR");resolve(thing.properties["outdoor_temperature"].getState().value);});'
                    },
                }
            }
        }
        
        self.add_param("temperature",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"],"Room's temperature","Temperatura della stanza");
        self.add_param("light",[25,80], ["LOW","MEDIUM","HIGH"],"Room's light","Luminosita' della stanza");
        self.add_param("time",[7,13,19,22], ["NIGHT","MORNING","AFTERNOON","EVENING","NIGHT"],"Time","Orario");
    
        self.add_param("outdoor_light",[25,80], ["LOW","MEDIUM","HIGH"], "Outdoor light","Luminosita' esterna")
        self.add_param("outdoor_temperature",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"], "Outdoor temperature","Temperatura esterna")

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
            nameL_handler += 'if(value < '+str(thresholds[i])+'){resolve("'+labels[i]+'");thing.invokeAction("mediate");return;}'

        nameL_handler += 'resolve("'+labels[len(thresholds)]+'");thing.invokeAction("mediate");';
        
        self.room["handlers"]["properties"][name+"L"]["write"] = nameL_handler

    def get_thing_description(self):
            return self.room

