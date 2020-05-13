import math

class Board:

    def __init__(self, name):

        self.td = {
            "thing":{
                "title": name,
                "description": "A board for announcements",
                "descriptions": {
                    "it": "Una lavagna per annunci"
                },
                "@context": "https://www.w3.org/2019/wot/td/v1",
                    "properties":{
                        "ads": {
                            "description": "List of ads",
                            "descriptions": {
                                "it": "La lista degli annunci"
                            },
                            "type":"array",
                            "readOnly":True,
                            "observable":"True"
                        }
                    },
                    "actions":{
                        "pubblish": {
                            "description": "Pubblish a new ads",
                            "descriptions": {
                                "it": "Pubblica un nuovo annuncio"
                            },
                            "input": {
                                "type": 'object',
                            },
                        }
                    },

                    "events": {
                        "ads": {
                            "description": "A new ads",
                            "descriptions": {
                                "it": "Un nuovo annuncio"
                            },
                            "data": {
                                "type": 'object',
                            },
                        } 
                    },
                },
                "initialScript":"thing.writeProperty('ads',[]);",
                "handlers":{
                    "actions":{
                        "pubblish":"thing.emitEvent('ads',input);resolve('Pubblished!');let data={}; data['data']=input;data['timestamp']=(new Date()).toISOString();thing.readProperty('ads').then((ls)=>{ls.push(data);thing.writeProperty('ads',ls);});",
                        },
                }
            }

    def get_thing_description(self):
        return self.td