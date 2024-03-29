
const code = ` 

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

            thing.expose().then(() => { console.info("Microbit \${thing.getThingDescription().title} ready!"); });

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

            thing.expose().then(() => { console.info("\${thing.getThingDescription().title} ready!"); });
        })
        .catch((e) => {
            console.log(e);
        });
}

//newRoom(129)
//newMicrobit(1252840479.9999999);
newMicrobit(671265031);
newMicrobit(20458004765.9999998);
newRoom(42)

`
WoTHelpers.fetch("http://131.114.73.148:2000/servient").then(async (td) => {
    // using await for serial execution (note 'async' in then() of fetch())
    try {
        let thing = await WoT.consume(td);

        thing.invokeAction("runPrivilegedScript",code)
    }
    catch (err) {
        console.error("Script error:", err);
    }
}).catch((err) => { console.error("Fetch error:", err); });

