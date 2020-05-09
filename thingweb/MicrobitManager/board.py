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
                "handlers":{
                    "actions":{
                        "pubblish":"thing.emitEvent('ads',input);resolve('Pubblished!');",
                        },
                }
            }

    def get_thing_description(self):
        return self.td