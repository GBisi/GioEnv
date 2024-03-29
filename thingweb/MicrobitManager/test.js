
const weatherapi = "http://api.weatherapi.com/v1/current.json?q=43,10&key=e5dec06056da4e81be1171342200504"

const openweathermap = "http://api.openweathermap.org/data/2.5/weather?units=metric&lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c"
const openweathermap_uvi = "http://api.openweathermap.org/data/2.5/uvi?lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c"

const fetch = require('node-fetch');

//https://github.com/lancaster-university/microbit-dal/blob/master/source/core/MicroBitDevice.cpp
function getFriendlyName(serial_number){
    
    var n = Math.ceil(serial_number)
    var name_len = 5
    var code_letters = 5
    var codebook = [
        ['z', 'v', 'g', 'p', 't'],
        ['u', 'o', 'i', 'e', 'a'],
        ['z', 'v', 'g', 'p', 't'],
        ['u', 'o', 'i', 'e', 'a'],
        ['z', 'v', 'g', 'p', 't']
    ]

    var ld = 1
    var d = code_letters
    var name = ""

    for (var i=0; i<name_len; i++){
        var h = Math.floor((n % d) / ld);
        n -= h;
        d *= code_letters;
        ld *= code_letters;
        name = codebook[i][h] + name
    }

    return name
}

function newMicrobit(serial){
    var t = WoT.produce({
        title: getFriendlyName(serial),
        description: "A Microbit Device",
        descriptions: {
            "it": "Un Microbit"
        },
        "@context": "https://www.w3.org/2019/wot/td/v1",
        properties: {
            serial_number: {
                type: "float",
                description: "This Microbit's serial number",
                descriptions: {
                    "it": "Numero seriale del Microbit"
                },
                observable: false,
                readOnly: true
            },
            light: {
                    type: "number",
                    description: "Value of this Microbit's light sensor",
                    descriptions: {
                        "it": "Valore del sensore di luminosita' di questo Microbit"
                    },
                    observable: true,
                    "#input":true
                    },
            temp: {
                    type: "number",
                    description: "Value of this Microbit's temp sensor",
                    descriptions: {
                        "it": "Valore del sensore di temperatura di questo Microbit"
                    },
                    observable: true,
                    "#input":true
                }
            }
        });
        
        t.then((thing) => {
            // init property values
            thing.writeProperty("serial_number", serial);
            thing.writeProperty("temp", 0);
            thing.writeProperty("light", 0);

            thing.expose().then(() => { console.info(`Microbit ${thing.getThingDescription().title} ready!`); });

        })
        .catch((e) => {
            console.log(e);
        });

        return t
            
}

function addParams(thing, name, thresholds, labels, description = "", descriptionIta = ""){

    thing["properties"][name] = {
        type:"number",
        description: description,
        descriptions: {
            "it": descriptionIta
        },
        observable: true,
        readOnly: true,
        "#input":true
    }

    thing["properties"][name+"L"] = {
        type:"string",
        description: description+" in levels",
        descriptions: {
            "it": descriptionIta+" in livelli"
        },
        observable: true,
        readOnly: true,
        enum:[...new Set(labels)],
    }

    handler = (thing,name) => {
        return (newValue) => {
        return new Promise((resolve, reject) => {
            thing.readProperty(name).then((val) => {

                value = labels[thresholds.length]

                for(var i=0; i<thresholds.length; i++){
                    if(val < thresholds[i]){
                        value = labels[i]
                        break
                    }
                }
                
                old = thing.readProperty(name+"L")
                if(value != old){
                     thing.writeProperty(name+"L", value);
                }

                thing.writeProperty("last_indoor_update", (new Date()).toISOString());

                resolve(newValue)

            });
        });
        
    }
};

    return handler

}

function getRoom(id){
    var room = {
        title: "room"+id,
        description: "A Smart Room",
        descriptions: {
            "it": "Una stanza intelligente"
        },
        "@context": "https://www.w3.org/2019/wot/td/v1",
        properties: {
            last_indoor_update: {
                    type: "string",
                    description: "Last room's sensors update",
                    descriptions: {
                        "it": "Ultimo aggiornamento dai sensori nella stanza"
                    },
                    observable: true,
                    readOnly: true
                },
                
            last_outdoor_update: {
                    type: "string",
                    description: "Last outdoor update",
                    descriptions: {
                        "it": "Ultimo aggiornamento dei parametri esterni"
                    },
                    observable: true,
                    readOnly: true
                }
        },
        actions:{
            refresh: {
                description: "Update the parameters",
                descriptions: {
                    "it": "Aggiorna i parametri"
                },
                output: { type: "object" }
            }
        },
        events: {
            fix: {
                description: "Some action to do",
                descriptions: {
                    "it": "Qualche azione da compiere"
                }
            }
        }
    };

    handlers = {}

    handlers["temp"]=addParams(room,"temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"],"Room's temperature","Temperatura della stanza");
    handlers["light"]=addParams(room,"light",[25,80], ["LOW","MEDIUM","HIGH"],"Room's light","Luminosita' della stanza");
    handlers["time"]=addParams(room,"time",[7,13,19,22], ["NIGHT","MORNING","AFTERNOON","EVENING","NIGHT"],"Time","Orario");
    
	handlers["outdoor_light"]=addParams(room,"outdoor_light",[25,80], ["LOW","MEDIUM","HIGH"], "Outdoor light","Luminosita' esterna")
	handlers["outdoor_temp"]=addParams(room,"outdoor_temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"], "Outdoor temperature","Temperatura esterna")
    
    return {"room":room,"handlers":handlers}
}

function newRoom(id){
    var val = getRoom(id)
    var room = val["room"]
    var handlers = val["handlers"]
    return WoT.produce(room).then((thing) => {

            Object.keys(handlers).forEach(function(key) {
                var value = handlers[key];
                thing.setPropertyWriteHandler(key, value(thing,key));
            }); 

            thing.setPropertyReadHandler("outdoor_temp", () => {
                return new Promise((resolve, reject) => {
                    fetch(openweathermap)
                        .then((response) => {
                            return response.json();
                        })
                        .then((data) => {
                            thing.writeProperty("last_outdoor_update", (new Date()).toISOString());
                            resolve(data["main"]["feels_like"])
                        });
                });
            });

            thing.setPropertyReadHandler("outdoor_light", () => {
                return new Promise((resolve, reject) => {
                    fetch(openweathermap_uvi)
                        .then((response) => {
                            return response.json();
                        })
                        .then((data) => {
                            thing.writeProperty("last_outdoor_update", (new Date()).toISOString());
                            resolve((data["value"]/11)*255)
                        });
                });
            });

            thing.setPropertyReadHandler("time", () => {
                return new Promise((resolve, reject) => {
                    resolve((new Date()).getHours())
                });
            });
            
            thing.setActionHandler("refresh", () => {
                return new Promise((resolve, reject) => {
                    thing.readAllProperties()
                        .then((map) => {resolve(map)})
                });
            });

            thing.writeProperty("temp", 0);
            thing.writeProperty("light", 0);
            thing.writeProperty("time", (new Date()).getHours());

            thing.writeProperty("outdoor_temp", 0);
            thing.writeProperty("outdoor_light", 0);

            thing.writeProperty("last_indoor_update", 0);
            thing.writeProperty("last_outdoor_update", 0);

            thing.expose().then(() => { console.info(`${thing.getThingDescription().title} ready!`); });
        })
        .catch((e) => {
            console.log(e);
        });
}

//newRoom(129)

var microbit = newMicrobit(384933164).then((thing) => {

    var td = thing.getThingDescription();
    WoT.consume(td).then((consumed)=>{
            consumed.updateProperty("serial_number",4.2);
            consumed.updateProperty("temp",-42);
            consumed.updateProperty("light",42);
            consumed.updateProperty("serial_number",4.2);
    })

});
/*
newMicrobit(1252840479.9999999);
//newMicrobit(671265031);
//newMicrobit(20458004765.9999998);
td = {
    "thing":{
       "title":"room42",
       "description":"A Smart Room",
       "descriptions":{
          "it":"Una stanza intelligente"
       },
       "@context":"https://www.w3.org/2019/wot/td/v1",
       "properties":{
          "last_indoor_update":{
             "type":"string",
             "description":"Last room's sensors update",
             "descriptions":{
                "it":"Ultimo aggiornamento dai sensori nella stanza"
             },
             "observable":true,
             "readOnly":true,
             "writeOnly":false,
             "#input":false,
             "#output":false
          },
          "last_outdoor_update":{
             "type":"string",
             "description":"Last outdoor update",
             "descriptions":{
                "it":"Ultimo aggiornamento dei parametri esterni"
             },
             "observable":true,
             "readOnly":true,
             "writeOnly":false,
             "#input":false,
             "#output":false
          },
          "temp":{
             "type":"number",
             "description":"Room's temperature",
             "descriptions":{
                "it":"Temperatura della stanza"
             },
             "observable":true,
             "readOnly":true,
             "#input":true,
             "writeOnly":false,
             "#output":false
          },
          "tempL":{
             "type":"string",
             "description":"Room's temperature in levels",
             "descriptions":{
                "it":"Temperatura della stanza in livelli"
             },
             "observable":true,
             "readOnly":true,
             "enum":[
                "VERY_LOW",
                "LOW",
                "MEDIUM",
                "HIGH",
                "VERY_HIGH"
             ],
             "writeOnly":false,
             "#input":false,
             "#output":false
          },
          "light":{
             "type":"number",
             "description":"Room's light",
             "descriptions":{
                "it":"Luminosita' della stanza"
             },
             "observable":true,
             "readOnly":true,
             "#input":true,
             "writeOnly":false,
             "#output":false
          },
          "lightL":{
             "type":"string",
             "description":"Room's light in levels",
             "descriptions":{
                "it":"Luminosita' della stanza in livelli"
             },
             "observable":true,
             "readOnly":true,
             "enum":[
                "LOW",
                "MEDIUM",
                "HIGH"
             ],
             "writeOnly":false,
             "#input":false,
             "#output":false
          },
          "time":{
             "type":"number",
             "description":"Time",
             "descriptions":{
                "it":"Orario"
             },
             "observable":true,
             "readOnly":true,
             "#input":true,
             "writeOnly":false,
             "#output":false
          },
          "timeL":{
             "type":"string",
             "description":"Time in levels",
             "descriptions":{
                "it":"Orario in livelli"
             },
             "observable":true,
             "readOnly":true,
             "enum":[
                "NIGHT",
                "MORNING",
                "AFTERNOON",
                "EVENING"
             ],
             "writeOnly":false,
             "#input":false,
             "#output":false
          },
          "outdoor_light":{
             "type":"number",
             "description":"Outdoor light",
             "descriptions":{
                "it":"Luminosita' esterna"
             },
             "observable":true,
             "readOnly":true,
             "#input":true,
             "writeOnly":false,
             "#output":false
          },
          "outdoor_lightL":{
             "type":"string",
             "description":"Outdoor light in levels",
             "descriptions":{
                "it":"Luminosita' esterna in livelli"
             },
             "observable":true,
             "readOnly":true,
             "enum":[
                "LOW",
                "MEDIUM",
                "HIGH"
             ],
             "writeOnly":false,
             "#input":false,
             "#output":false
          },
          "outdoor_temp":{
             "type":"number",
             "description":"Outdoor temperature",
             "descriptions":{
                "it":"Temperatura esterna"
             },
             "observable":true,
             "readOnly":true,
             "#input":true,
             "writeOnly":false,
             "#output":false
          },
          "outdoor_tempL":{
             "type":"string",
             "description":"Outdoor temperature in levels",
             "descriptions":{
                "it":"Temperatura esterna in livelli"
             },
             "observable":true,
             "readOnly":true,
             "enum":[
                "VERY_LOW",
                "LOW",
                "MEDIUM",
                "HIGH",
                "VERY_HIGH"
             ],
             "writeOnly":false,
             "#input":false,
             "#output":false
          }
       },
       "actions":{
          "refresh":{
             "description":"Update the parameters",
             "descriptions":{
                "it":"Aggiorna i parametri"
             },
             "output":{
                "type":"object"
             }
          }
       },
       "events":{
          "fix":{
             "description":"Some action to do",
             "descriptions":{
                "it":"Qualche azione da compiere"
             }
          }
       }
    },
    "initialScript":"const fetch = require('node-fetch');",
    "endScript":"thing.writeProperty(\"temp\", 0); thing.writeProperty(\"light\", 0);thing.writeProperty(\"time\", (new Date()).getHours());thing.writeProperty(\"outdoor_temp\", 0);thing.writeProperty(\"outdoor_light\", 0); thing.writeProperty(\"last_indoor_update\", 0); thing.writeProperty(\"last_outdoor_update\", 0);",
    "handlers":{
       "actions":{
          "refresh":"thing.readAllProperties().then((map) => {resolve(map)})"
       },
       "properties":{
          "outdoor_temp":{
             "read":"fetch(\"http://api.openweathermap.org/data/2.5/weather?units=metric&lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c\").then((response) => {return response.json(); }).then((data) => {thing.writeProperty(\"last_outdoor_update\", (new Date()).toISOString());resolve(data[\"main\"][\"feels_like\"]) });"
          },
          "outdoor_light":{
             "read":"fetch(\"http://api.openweathermap.org/data/2.5/uvi?lat=43&lon=10&appid=647aa595e78b34e517dad92e1cf5e65c\").then((response) => {return response.json();}).then((data) => {thing.writeProperty(\"last_outdoor_update\", (new Date()).toISOString());resolve((data[\"value\"]/11)*255)});"
          }
       }
    }
 }
WoT.add("http://131.114.73.148:2000",td);
WoT.delete("http://131.114.73.148:2000","tetoz");

*/


let user_setup = {
    'temperature': [],
    'light': []
};
let mediation = {
    'temperature': 'medium',
    'light': 'medium'
};
let light = 0;
let temp = 0;
let arr = [];
thing.readAllProperties().then((props) => {
    delete props['temperature_microbit'];
    delete props['light_microbit'];
    delete props['last_indoor_update'];
    delete props['last_outdoor_update'];
    props['users'] = Object.keys(props['users']).length;
    props['light'] = props['lightL'].toLowerCase();
    props['temperature'] = props['temperatureL'].toLowerCase();
    light = props['light'];
    temp = props['temperature'];
    let facts = '[' + jsontolist(props).join().toLowerCase() + ']';
    console.debug('*** MEDIATE ***:' + facts);
    thing.readProperty('users').then((users) => {
        users_len = props['users'];
        if (users_len == 0) {
            console.debug('*** MEDIATE ***: no user');
            resolve(mediation);
            return;
        }
        for (const user in users) {
            sleep(1000).then(()=>{
            console.debug('*** MEDIATE ***: preferences of ' + user + ' getting');
            fetch(eaas + 'infer', {
                'method': 'POST',
                'headers': {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                'body': JSON.stringify({
                    'rules': users[user]['rules'],
                    'facts': facts
                })
            }).then((response) => {
                return response.json();
            }).then((data) => {
                console.debug('*** MEDIATE ***: preferences of ' + user + ' -> ' + JSON.stringify(data));
                actions = data['actions'];
                actions = listtojson(actions);
                if (!('light' in actions)) {
                    actions['light'] = light
                }
                if (!('temperature' in actions)) {
                    actions['temperature'] = temp
                };
                user_setup['temperature'].push(actions['temperature']);
                user_setup['light'].push(actions['light']);
                return user_setup
            }).catch((e) => {
                console.debug(e);
                users_len--;
                return user_setup;
            }).then((data) => {
                if (data['temperature'].length >= users_len) {
                    console.debug('*** MEDIATE ***: total preferences ' + JSON.stringify(data));
                    console.debug('*** MEDIATE ***: mediating');
                        fetch(eaas + 'mediate/avg', {
                        'method': 'POST',
                        'headers': {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        'body': JSON.stringify({
                            'rounding': 'floor',
                            'data': data['temperature'],
                            'values': ['very_low', 'low', 'medium', 'high', 'very_high']
                        })
                    }).then((response) => {
                        return response.json();
                    }).then((data) => {
                        console.debug('*** MEDIATE ***: temp ' + JSON.stringify(data));
                        mediation['temperature'] = data['avg']
                    }).catch((e) => {
                        console.debug(e);
                    }).then(fetch(eaas + 'mediate/avg', {
                        'method': 'POST',
                        'headers': {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        'body': JSON.stringify({
                            'data': data['light'],
                            'values': ['low', 'medium', 'high'],
                            'rounding': 'floor'
                        })
                    }).then((response) => {
                        return response.json();
                    }).then((data) => {
                        console.debug('*** MEDIATE ***: light ' + JSON.stringify(data));
                        mediation['light'] = data['avg'];
                        console.debug('*** MEDIATE ***: result ' + JSON.stringify(mediation));
                        resolve(mediation);
                        fetch('"+temperature_microbit+"/actions/set_temperature', {
                            'method': 'POST',
                            'headers': {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                            'body': JSON.stringify({
                                'room': '"+self.number+"',
                                'temperature': mediation['temperature']
                            })
                        });
                        fetch('"+light_microbit+"/actions/set_light', {
                            'method': 'POST',
                            'headers': {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                            'body': JSON.stringify({
                                'room': '"+self.number+"',
                                'light': mediation['light']
                            })
                        })
                 
                    }));
                }
            });
            }).catch((e) => {
                console.debug(e);
            });
        };
    });
});



let user_setup = {
    'temperature': [],
    'light': []
};
let mediation = {'temperature': 'medium','light': 'low'};
let light = 0;
let temp = 0;
let arr = [];
thing.readAllProperties().then((props) => {
    delete props['temperature_microbit'];
    delete props['light_microbit'];
    delete props['last_indoor_update'];
    delete props['last_outdoor_update'];
    props['users'] = Object.keys(props['users']).length;
    props['light'] = props['lightL'].toLowerCase();
    props['temperature'] = props['temperatureL'].toLowerCase();
    light = props['light'];
    temp = props['temperature'];
    let facts = '[' + jsontolist(props).join().toLowerCase() + ']';
    console.debug('*** MEDIATE ***:' + facts);
    thing.readProperty('users').then((users) => {
        users_len = props['users'];
        if (users_len == 0) {
            console.debug('*** MEDIATE ***: no user');
            resolve(mediation);
            return;
        }
        let timeWait = 0;
        for (const user in users) {
            timeWait++;
            sleep(timeWait * 500).then(() => {
                console.debug('*** MEDIATE ***: preferences of ' + user + ' getting');
                fetch(eaas + 'infer', {
                    'method': 'POST',
                    'headers': {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    'body': JSON.stringify({
                        'rules': users[user]['rules'],
                        'facts': facts
                    })
                }).then((response) => {
                    return response.json();
                }).then((data) => {
                    console.debug('*** MEDIATE ***: preferences of ' + user + ' -> ' + JSON.stringify(data));
                    actions = data['actions'];
                    actions = listtojson(actions);
                    if (!('light' in actions)) {
                        actions['light'] = light
                    }
                    if (!('temperature' in actions)) {
                        actions['temperature'] = temp
                    };
                    user_setup['temperature'].push(actions['temperature']);
                    user_setup['light'].push(actions['light']);
                    return user_setup
                }).catch((e) => {
                    console.debug(e);
                    users_len--;
                    return user_setup;
                }).then((data) => {
                    if (data['temperature'].length >= users_len) {
                        console.debug('*** MEDIATE ***: total preferences ' + JSON.stringify(data));
                        console.debug('*** MEDIATE ***: mediating');
                        fetch(eaas + 'mediate/avg', {
                            'method': 'POST',
                            'headers': {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                            'body': JSON.stringify({
                                'rounding': 'floor',
                                'data': data['temperature'],
                                'values': ['very_low', 'low', 'medium', 'high', 'very_high']
                            })
                        }).then((response) => {
                            return response.json();
                        }).then((data) => {
                            console.debug('*** MEDIATE ***: temp ' + JSON.stringify(data));
                            mediation['temperature'] = data['avg']
                        }).catch((e) => {
                            console.debug(e);
                        }).then(fetch(eaas + 'mediate/avg', {
                            'method': 'POST',
                            'headers': {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                            'body': JSON.stringify({
                                'data': data['light'],
                                'values': ['low', 'medium', 'high'],
                                'rounding': 'floor'
                            })
                        }).then((response) => {
                            return response.json();
                        }).then((data) => {
                            console.debug('*** MEDIATE ***: light ' + JSON.stringify(data));
                            mediation['light'] = data['avg'];
                            console.debug('*** MEDIATE ***: result ' + JSON.stringify(mediation));
                            resolve(mediation);
                            fetch('"+temperature_microbit+"/actions/set_temperature', {
                                'method': 'POST',
                                'headers': {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json'
                                },
                                'body': JSON.stringify({
                                    'room': '"+self.number+"',
                                    'temperature': mediation['temperature']
                                })
                            });
                            fetch('"+light_microbit+"/actions/set_light', {
                                'method': 'POST',
                                'headers': {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json'
                                },
                                'body': JSON.stringify({
                                    'room': '"+self.number+"',
                                    'light': mediation['light']
                                })
                            })
                        }));
                    }
                });
            }).catch((e) => {
                console.debug(e);
            });
        };
    });
});

let mediation = {
    'temperature': 'medium',
    'light': 'low'
};
thing.readProperty('rooms').then((rooms) => {
            if (Object.keys(rooms).length == 0) {
                console.debug('*** MEDIATE ***: no rooms');
                resolve(mediation);
                return;
            };
            let pref = {
                'temperature': [],
                'light': []
            };
            for (const r in rooms) {
                pref['temperature'].push(rooms[r]['temperature']);
                pref['light'].push(rooms[r]['light']);
            };
            console.debug('*** MEDIATE ***: total preferences ' + JSON.stringify(pref));
            console.debug('*** MEDIATE ***: mediating');
            fetch(eaas + 'mediate/avg', {
                    'method': 'POST',
                    'headers': {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    'body': JSON.stringify({
                        'rounding': 'floor',
                        'data': pref['temperature'],
                        'values': ['very_low', 'low', 'medium', 'high', 'very_high']
                    })
                }).then((response) => {
                    return response.json();
                }).then((data) => {
                    console.debug('*** MEDIATE ***: temp ' + JSON.stringify(data));
                    mediation['temperature'] = data['avg']
                }).catch((e) => {
                    console.debug(e);
                }).then(()=>{
                    fetch(eaas + 'mediate/avg', {
                        'method': 'POST',
                        'headers': {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        'body': JSON.stringify({
                            'data': data['light'],
                            'values': ['low', 'medium', 'high'],
                            'rounding': 'floor'
                        })
                    }).then((response) => {
                        return response.json();
                    }).then((data) => {
                        console.debug('*** MEDIATE ***: light ' + JSON.stringify(data));
                        mediation['light'] = data['avg'];
                        console.debug('*** MEDIATE ***: result ' + JSON.stringify(mediation));
                        resolve(mediation);
                    });
                }).catch(()=>{console.debug("Error during mediation"); resolve(mediation);})
            });
                    

                    fetch(s2m+'Admin/rules').then(function(response) {
                        return response.json()
                    }).then(function(data) {
                        let rules = JSON.stringify({
                            'rules': data['data']
                        });
                        return fetch(eaas + 'parse/rulestolist', {
                            'method': 'POST',
                            'headers': {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                            'body': rules
                        })
                    }).then(function(response) {
                        return response.json();
                    }).then(function(data) {
                        fetch(eaas + 'infer', {
                            'method': 'POST',
                            'headers': {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                            'body': JSON.stringify({
                                'rules': data["rules"],
                                'facts': jsontolist(input)
                            })
                        }).then((response) => {
                            return response.json();
                        }).then((data) => {resolve(data);});
                    }).catch(function(error) {
                        console.debug(error);
                        resolve("Unable to deploy");
                    });


                    
            