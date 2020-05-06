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
                        },
                        "set_light": {
                                "description": "Request a new light settings",
                                "descriptions": {
                                    "it": "Richiedi nuova impostazione della luce"
                                },
                                "input": { "type": "object" },
                            },
                        "mediateRooms": {
                            "description": "Mediate rooms preferences",
                            "descriptions": {
                                "it": "Media tra le preferenze delle stanze"
                            },
                                "output": { "type": "object" }
                        },
                        "deploy": {
                            "description": "Mediate microbit's preferences with Admin",
                            "descriptions": {
                                "it": "Media tra le preferenze del microbit e l'Admin"
                            },
                                "output": { "type": "object" }
                            }
                    },

                    "events": {
                        "setup": {
                            "description": "A new setup of the enviroment",
                            "descriptions": {
                                "it": "un nuovo setup dell'ambiente"
                            },
                            "data": {
                                "type": 'object',
                            },
                        } 
                    },
                },
                "initialScript":'const fetch = require("node-fetch");const eaas = "http://131.114.73.148:1999/";const s2m = "http://131.114.73.148:2048/";thing.writeProperty("rooms",{});thing.writeProperty("serial_number", '+str(serial_number)+');thing.writeProperty("temp", 0);thing.writeProperty("light", 0);function jsontolist(obj){ls = [];for(key in obj){val = obj[key];if(typeof val === "object"){val = jsontolist(val)}ls.push(key +"("+val+")")}return ls};function listtojson(ls){obj={};if(ls != "[]" && ls !=""){ls = ls.replace("[","").replace("]","").split(", ");for(let elem in ls){elem=ls[elem].split("(");name = elem[0];value=elem[1];obj[name]=value.replace(")","")}}return obj};',
                "handlers":{
                    "actions":{
                        "set_light":"thing.readProperty('rooms').then((rooms)=>{if(!(input['room'] in rooms)){rooms[input['room']]={'temperature':'medium', 'light':'low'}}; if(!('light' in input)){resolve('Malformed request');return;} rooms[input['room']]['light'] = input['light']; thing.writeProperty('rooms',rooms); resolve('Request added'); thing.invokeAction('mediateRooms');}).catch((e)=>{console.debug(e); resolve('Malformed request');});",
                        "set_temperature":"thing.readProperty('rooms').then((rooms)=>{if(!(input['room'] in rooms)){rooms[input['room']]={'temperature':'medium', 'light':'low'}}; if(!('temperature' in input)){resolve('Malformed request');return;} rooms[input['room']]['temperature'] = input['temperature']; thing.writeProperty('rooms',rooms); resolve('Request added'); thing.invokeAction('mediateRooms');}).catch((e)=>{console.debug(e); resolve('Malformed request');});",
                        "mediateRooms":"let mediation = { 'temperature': 'medium', 'light': 'low' }; thing.readProperty('rooms').then((rooms) => { if (Object.keys(rooms).length == 0) { console.debug('*** MEDIATE ROOMS "+self.friendly_name+" ***: no rooms'); resolve(mediation); return; }; let pref = { 'temperature': [], 'light': [] }; for (const r in rooms) { pref['temperature'].push(rooms[r]['temperature']); pref['light'].push(rooms[r]['light']); }; console.debug('*** MEDIATE ROOMS "+self.friendly_name+" ***: total preferences ' + JSON.stringify(pref)); console.debug('*** MEDIATE ROOMS "+self.friendly_name+" ***: mediating'); fetch(eaas + 'mediate/avg', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'rounding': 'floor', 'data': pref['temperature'], 'values': ['very_low', 'low', 'medium', 'high', 'very_high'] }) }).then((response) => { return response.json(); }).then((data) => { console.debug('*** MEDIATE ROOMS "+self.friendly_name+" ***: temp ' + JSON.stringify(data)); mediation['temperature'] = data['avg'] }).catch((e) => { console.debug(e); }).then(()=>{ fetch(eaas + 'mediate/avg', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'data': pref['light'], 'values': ['low', 'medium', 'high'], 'rounding': 'floor' }) }).then((response) => { return response.json(); }).then((data) => { console.debug('*** MEDIATE ROOMS "+self.friendly_name+" ***: light ' + JSON.stringify(data)); mediation['light'] = data['avg']; console.debug('*** MEDIATE ROOMS "+self.friendly_name+" ***: result ' + JSON.stringify(mediation)); resolve(mediation); thing.invokeAction('deploy',mediation); }); }).catch((e)=>{console.debug(e); resolve(mediation); thing.invokeAction('deploy',mediation); }) });",
                        "deploy":"console.debug('*** DEPLOY "+self.friendly_name+" ***: start'); console.debug('*** DEPLOY "+self.friendly_name+" ***: getting admin rules'); fetch(s2m+'Admin/rules').then(function(response) { return response.json() }).then(function(data) { let rules = JSON.stringify({ 'rules': data['data'] }); console.debug('*** DEPLOY "+self.friendly_name+" ***: parsing admin rules'); return fetch(eaas + 'parse/rulestolist', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': rules }) }).then(function(response) { return response.json(); }).then(function(data) {  let facts = '[' + jsontolist(input).join().toLowerCase() + ']'; console.debug('*** DEPLOY "+self.friendly_name+" ***: state '+facts); fetch(eaas + 'infer', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'rules': data['rules'], 'facts': facts }) }).then((response) => { return response.json(); }).then((data) => { console.debug('*** DEPLOY "+self.friendly_name+" ***: '+data['actions']); let actions = listtojson(data['actions']); resolve(actions); thing.emitEvent('setup',actions);}); }).catch(function(error) { console.debug(error); resolve('*** DEPLOY "+self.friendly_name+" ***: Unable to deploy'); }); ",
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