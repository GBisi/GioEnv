import math

class Mediator:

    def __init__(self):

        self.td = {
            "thing":{
                "title": "mediator",
                "description": "The Mediator",
                "descriptions": {
                    "it": "Il Mediatore"
                },
                "@context": "https://www.w3.org/2019/wot/td/v1",
                    "properties":{
                        "rooms": {
                            "description": "Rooms' list and their info",
                            "descriptions": {
                                "it": "La lista delle stanze e delle loro informazioni"
                            },
                            "type":"object",
                            "readOnly":True,
                            "observable":True
                        },
                        "users": {
                            "description": "Users' list and their rules",
                            "descriptions": {
                                "it": "La lista degli utenti e delle loro preferenze"
                            },
                            "type":"object",
                            "readOnly":True,
                            "observable":True
                        }
                    },
                    "actions":{
                        "setRules": {
                            "description": "Set the rules of a user",
                            "descriptions": {
                                "it": "Imposta le regole di un utente"
                            },
                            "input": { "type": "object" }
                        },
                        "getRules": {
                            "description": "Get the rules of a user",
                            "descriptions": {
                                "it": "Ottieni le regole di un utente"
                            },
                            "input": { "type": "string" }
                        },
                        "mediate": {
                            "description": "Starts a new mediation process",
                            "descriptions": {
                                "it": "Avvia un nuovo processo di mediazione"
                            },
                            "input": {
                                "type": 'object',
                            },
                        },
                        "solve": {
                            "description": "Solve all conflicts",
                            "descriptions": {
                                "it": "Risolve tutti i conflitti"
                            },
                            "input": {
                                "type": 'object',
                            },
                        },
                        "deploy": {
                            "description": "Deploy the decisions",
                            "descriptions": {
                                "it": "Effettua le decisioni"
                            },
                            "input": {
                                "type": 'array',
                            },
                        }
                    },
                    "events": {
                        "decisions": {
                            "description": "A new set of decisions",
                            "descriptions": {
                                "it": "Un nuovo insieme di decisioni"
                            },
                            "data": {
                                "type": 'object',
                            },
                        } 
                    },
                },
                "initialScript":"thing.writeProperty('rooms',{});thing.writeProperty('users',{});const fetch = require('node-fetch');const s2m = 'http://131.114.73.148:2048/'; const eaas = 'http://131.114.73.148:1999/'; function removeItem(array, item) { var i = array.length; while (i--) { if (array[i] === item) { array.splice(array.indexOf(item), 1); } } return array; } ",
                "handlers":{
                    "actions":{
                        "setRules":"fetch(s2m+input['id']+'/rules', { 'method': 'PUT', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': input['rules'] }).then(()=>{resolve('Rules setted'); thing.invokeAction('getRules',input['id']); thing.invokeAction('solve');}).catch(function(error) { console.debug(error); resolve('Error: user rules not updated'); });",
                        "getRules":"thing.readProperty('users').then((users) => {fetch(s2m + input + '/rules').then(function(response) { return response.json() }).then(function(data) {  users[input] = data['data']; resolve('User rules getted');}).catch(function(error) { console.debug(error); resolve('Error: user rules not getted'); }); });",
                        "mediate":"thing.readProperty('rooms').then((rooms) => {if (!(rooms.hasOwnProperty(input['room']['number']))) {rooms[input['room']['number']] = {};  } rooms[input['room']['number']]['facts'] = input['room']['facts']; let users = input['room']['users']; rooms[input['room']['number']]['users'] = users; for(u in users){thing.invokeAction('getRules',users[u]);} resolve('OK'); thing.invokeAction('getRules',users[users.length-1]).then(()=>{ thing.invokeAction('getRules','Admin').then(()=>{thing.invokeAction('solve');})}); });",
                        "solve":"console.debug('Solving...');thing.readProperty('rooms').then((rooms) => { inUsers=[]; facts=[]; for(r in rooms){facts=facts.concat(rooms[r]['facts']);inUsers=inUsers.concat(rooms[r]['users'])} console.debug(facts); console.debug(inUsers); thing.readProperty('users').then((users) => { inUsersRules=''; for(u in inUsers){inUsersRules+=users[inUsers[u]]+'\\n';} inUsersRules+=users['Admin']+'\\n'; console.debug(inUsersRules); fetch(eaas + 'decide', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'facts': facts, 'policies': inUsersRules, 'goals': 'go. todo(A,B,C).' }) }).then((response) => { return response.json(); }).then((data) => { thing.invokeAction('deploy',removeItem(data['decisions'],'go')) }) }); });",
                        "deploy":"console.debug('Decisions:');console.debug(input);for (i in input) { cmd = input[i]; if (cmd.startsWith('todo(')) { cmd = cmd.replace('todo(', '').replace(')', '').split(','); fetch('http://131.114.73.148:2000/' + cmd[0] + '/actions/set', { 'method': 'POST', 'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }, 'body': JSON.stringify({ 'param': cmd[1], 'val': cmd[2] }) }) } }"
                        },
                }
            }

    def get_thing_description(self):
        return self.td