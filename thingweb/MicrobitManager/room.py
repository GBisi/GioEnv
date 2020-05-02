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
                        },

                    "users": {
                        "type":"object",
                        "description": "Users in the room with their preferences",
                            "descriptions": {
                                "it": "Utenti nella stanza con le loro preferenze"
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
                    "mediateUsers": {
                        "description": "Mediate user's preferences",
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
            "initialScript":'const eaas = "http://131.114.73.148:1999/";const s2m = "http://131.114.73.148:2048/";const fetch = require("node-fetch");const weatherapi = "https://api.weatherapi.com/v1/current.json?q=43,10&key=e5dec06056da4e81be1171342200504";const openweathermap = "https://api.openweathermap.org/data/2.5/weather?units=metric&lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c";const openweathermap_uvi = "https://api.openweathermap.org/data/2.5/uvi?lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c";function listtojson(ls){obj={};if(ls != "[]" && ls !=""){ls = ls.replace("[","").replace("]","").split(", ");for(let elem in ls){elem=ls[elem].split("(");name = elem[0];value=elem[1];obj[name]=value.replace(")","")}}return obj};function jsontolist(obj){ls = [];for(key in obj){val = obj[key];if(typeof val === "object"){val = jsontolist(val)}ls.push(key +"("+val+")")}return ls};',
            "endScript":"thing.writeProperty('users', {});thing.writeProperty('temperature', 0);thing.writeProperty('light', 0);thing.writeProperty('time', (new Date()).getHours());thing.writeProperty('outdoor_temperature', 0);thing.writeProperty('outdoor_light', 0);thing.writeProperty('last_indoor_update', 0);thing.writeProperty('last_outdoor_update', 0);",
            "handlers":{
                "actions":{
                    "refresh":"thing.readAllProperties().then((map) => {resolve(map)})",
                    "enter":"thing.readProperty('users').then((users) => {if (!(users.hasOwnProperty(input))) {users[input] = {'rules':'[]'}; fetch(s2m + input + '/rules').then(function(response){return response.json()}).then(function(data){let rules = JSON.stringify({'rules':data['data']});return fetch(eaas + 'parse/rulestolist', {'method': 'POST','headers':{'Accept': 'application/json','Content-Type': 'application/json'},'body': rules})}).then(function(response){return response.json();}).then(function(data){users[input]=data; resolve('User registered')}).catch(function(error){console.debug(error);resolve('User registered');});}else{resolve('User already in the room');};});", 
                    "leave":"thing.readProperty('users').then((users) => {if(users.hasOwnProperty(input)){delete users[input];resolve('User removed');}else{resolve('User not in the room');}});",
                    "mediateUsers":"let user_setup = { 'temperature': [], 'light': [] }; let light = 0; let temp = 0; let arr = []; thing.readAllProperties().then((props) => { props['light'] = props['lightL'].toLowerCase(); props['temperature'] = props['temperatureL'].toLowerCase(); light = props['light']; temp = props['temperature']; let facts = '[' + jsontolist(props).join().toLowerCase() + ']'; thing.readProperty('users').then((users) => { users_len = Object.keys(props['users']).length; if (users_len == 0) { resolve(user_setup); return; } for (const user in users) { fetch(eaas + 'infer', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'rules': users[user]['rules'], 'facts': facts }) }).then((response) => { return response.json(); }).then((data) => { actions = data['actions']; actions = listtojson(actions); if (!('light' in actions)) { actions['light'] = light } if (!('temperature' in actions)) { actions['temperature'] = temp }; user_setup['temperature'].push(actions['temperature']); user_setup['light'].push(actions['light']); return user_setup }).catch((e) => { console.debug(e); users_len--; return user_setup; }).then((data) => { if (data['temperature'].length >= users_len) { return data; } }).then((data)=>{ fetch(eaas + 'mediate/avg', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'data':user_setup['temperature'], 'values':['very_low','low','medium','high','very_high'] }) }) }).then((response) => { return response.json(); }).then((data) => { resolve(data) }).catch((e) => { console.debug(e); }); }; }); });"
                    },
                
                "properties":{
                    "time":{
                        "read":"resolve((new Date()).getHours())"
                    },
                    "outdoor_light":{
                        "read":'fetch(openweathermap_uvi).then((response) => {return response.json();}).then((data) => {thing.writeProperty("last_outdoor_update", (new Date()).toISOString());resolve(((data["value"])/11)*255)}).catch((e)=>{});'
                    },
                    "outdoor_temperature":{
                        "read":'fetch(openweathermap).then((response) => {return response.json();}).then((data) => {thing.writeProperty("last_outdoor_update", (new Date()).toISOString());resolve(data["main"]["feels_like"])}).catch((e)=>{});'
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
            nameL_handler += 'if(value < '+str(thresholds[i])+'){resolve("'+labels[i]+'");return;}'

        nameL_handler += 'resolve("'+labels[len(thresholds)]+'");'
        
        self.room["handlers"]["properties"][name+"L"]["write"] = nameL_handler

    def get_thing_description(self):
            return self.room
        
