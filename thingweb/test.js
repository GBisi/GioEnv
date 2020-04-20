
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
    WoT.produce({
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
                    readOnly: true
                },
            temp: {
                    type: "number",
                    description: "Value of this Microbit's temp sensor",
                    descriptions: {
                        "it": "Valore del sensore di temperatura di questo Microbit"
                    },
                    observable: true,
                    readOnly: true
                }
            }
        }).then((thing) => {
            // init property values
            thing.writeProperty("serial_number", serial);
            thing.writeProperty("temp", 0);
            thing.writeProperty("light", 0);

            thing.expose().then(() => { console.info(`Microbit ${thing.getThingDescription().title} ready!`); });
        })
        .catch((e) => {
            console.log(e);
        });
            
}

function addParams(thing, name, thresholds, labels, description = "", descriptionIta = ""){

    thing["properties"][name] = {
        type:"number",
        description: description,
        descriptions: {
            "it": descriptionIta
        },
        observable: true,
        readOnly: true
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
        
        events: {
        fix: {
            description: "Some action to do",
            descriptions: {
                "it": "Qualche azione da compiere"
            }
        }
    }
    };

    addParams(room,"temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"],"Room's temperature","Temperatura della stanza");
    addParams(room,"light",[25,80], ["LOW","MEDIUM","HIGH"],"Room's light","Luminosita' della stanza");
    addParams(room,"time",[7,13,19,22], ["NIGHT","MORNING","AFTERNOON","EVENING","NIGHT"],"Time","Orario");
    
	addParams(room,"outdoor_light",[25,80], ["LOW","MEDIUM","HIGH"], "Outdoor light","Luminosita' esterna")
	addParams(room,"outdoor_temp",[18,20,22,24], ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"], "Outdoor temperature","Temperatura esterna")
    
    return room
}

function handler (thing,name) {
    function f() {
        return new Promise((resolve, reject) => {
            thing.readProperty(name).then((val) => {
                console.log(name)
                console.log(newValue)
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


            }).then(resolve()).catch();
        });
    }
    return f
}

function newRoom(id){
    var room = getRoom(id)
    WoT.produce(room).then((thing) => {

            thing.setPropertyWriteHandler("temp",handler(thing,"temp"))
            thing.writeProperty("temp", 0);
            thing.writeProperty("light", 0);
            thing.writeProperty("time", (new Date()).toISOString());

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

newRoom(129)

newMicrobit(384933164);
//newMicrobit(1252840479.9999999);
//newMicrobit(671265031);
//newMicrobit(20458004765.9999998);