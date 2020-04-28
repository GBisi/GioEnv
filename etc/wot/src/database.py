from errors import DatabaseError

class Database:

    def __init__(self, prefix = "localhost:5000/things/"):
        self.things = {}
        self.prefix = prefix
        print("DATABASE ONLINE @",prefix)

    def get_prefix():
        return self.prefix

    def add_thing(self, thing):

        thing.set_href_prefix(self.prefix+thing.get_id())

        if thing.get_id() in self.things:
            raise DatabaseError()
        else:
            self.things[thing.get_id()] = thing

    def remove_thing(self, thing):

        if thing.get_id() in self.things:
            del self.things[thing.get_id()]
        else:
            raise DatabaseError()

    def get_thing(self, id_):

        return self.things.get(id_, None)

    def get_things(self):
        things = []
        for thing in self.things.values():
            things.append(thing)

        return things
"""
        class OverheatedEvent(Event):

            def __init__(self, thing, data):
                Event.__init__(self, thing, 'overheated', data=data)


        class FadeAction(Action):

            def __init__(self, thing, input_):
                Action.__init__(self, uuid.uuid4().hex, thing, 'fade', input_=input_)

            def perform_action(self):
                time.sleep(self.input['duration'] / 1000)
                self.thing.set_property('brightness', self.input['brightness'])
                self.thing.add_event(OverheatedEvent(self.thing, 102))


        class ExampleDimmableLight(Thing):
           #A dimmable light that logs received commands to stdout.

            def __init__(self):
                Thing.__init__(
                    self,
                    'lamp',
                    'My Lamp',
                    'A web connected lamp',
                    'https://iot.mozilla.org/schemas',
                    ['OnOffSwitch', 'Light'],
                )

                self.add_property(
                    Property(self,
                            'on',
                            Value(True, lambda v: print('On-State is now', v)),
                            metadata={
                                '@type': 'OnOffProperty',
                                'title': 'On/Off',
                                'type': 'boolean',
                                'description': 'Whether the lamp is turned on',
                            }))

                self.add_property(
                    Property(self,
                            'brightness',
                            Value(50, lambda v: print('Brightness is now', v)),
                            metadata={
                                '@type': 'BrightnessProperty',
                                'title': 'Brightness',
                                'type': 'integer',
                                'description': 'The level of light from 0-100',
                                'minimum': 0,
                                'maximum': 100,
                                'unit': 'percent',
                            }))

                self.add_available_action(
                    'fade',
                    {
                        'title': 'Fade',
                        'description': 'Fade the lamp to a given level',
                        'input': {
                            'type': 'object',
                            'required': [
                                'brightness',
                                'duration',
                            ],
                            'properties': {
                                'brightness': {
                                    'type': 'integer',
                                    'minimum': 0,
                                    'maximum': 100,
                                    'unit': 'percent',
                                },
                                'duration': {
                                    'type': 'integer',
                                    'minimum': 1,
                                    'unit': 'milliseconds',
                                },
                            },
                        },
                    },
                    FadeAction)

                self.add_available_event(
                    'overheated',
                    {
                        'description':
                        'The lamp has exceeded its safe operating temperature',
                        'type': 'number',
                        'unit': 'degree celsius',
                    })


        class FakeGpioHumiditySensor(Thing):
            #A humidity sensor which updates its measurement every few seconds

            def __init__(self):
                Thing.__init__(
                    self,
                    'sensor',
                    'My Humidity Sensor',
                    'A web connected humidity sensor',
                    'https://iot.mozilla.org/schemas',
                    ['MultiLevelSensor']
                )

                self.level = Value(0.0)
                self.add_property(
                    Property(self,
                            'level',
                            self.level,
                            metadata={
                                '@type': 'LevelProperty',
                                'title': 'Humidity',
                                'type': 'number',
                                'description': 'The current humidity in %',
                                'minimum': 0,
                                'maximum': 100,
                                'unit': 'percent',
                                'readOnly': True,
                            }))

                logging.debug('starting the sensor update looping task')
                self.timer = Timer(self.update_level, 5000)
                self.stop_flag = self.timer.get_flag()
                #self.timer.start() #!

            def update_level(self):
                new_level = self.read_from_gpio()
                logging.debug('setting new humidity level: %s', new_level)
                self.level.notify_of_external_update(new_level)

            def cancel_update_level_task(self):
                self.stop_flag.set()

            @staticmethod
            def read_from_gpio():
                #Mimic an actual sensor updating its reading every couple seconds
                return abs(70.0 * random.random() * (-0.5 + random.random()))

        # Create a thing that represents a dimmable light
        light = ExampleDimmableLight()

        # Create a thing that represents a humidity sensor
        sensor = FakeGpioHumiditySensor()

        self.add_thing(light)
        self.add_thing(sensor)


    #needs database of action/event/property/value
    Why? put in properties
         post in things
    @staticmethod
    def decode(json):
    
        if "id" in json:
            id_ = json["id"]
        else:
            return None

        if "title" in json:
            title = json["title"]
        else:
            return None

        if "description" in json:
            description = json["description"]
        else:
            description = ''

        if "@context" in json:
            context = json["@context"]
        else:
            context = ''

        if "@type" in json:
            type_ = json["@type"]
        else:
            type_ = []

        if "prefix" in json:
            prefix = json["prefixn"]
        else:
            prefix = ''

        thing = Thing(id_, title, description, context, type_, prefix)
        
        return thing


txt = '{ "@context": "https://iot.mozilla.org/schemas", "@type": [ "OnOffSwitch", "Light" ], "actions": { "fade": { "description": "Fade the lamp to a given level", "input": { "properties": { "brightness": { "maximum": 100, "minimum": 0, "type": "integer", "unit": "percent" }, "duration": { "minimum": 1, "type": "integer", "unit": "milliseconds" } }, "required": [ "brightness", "duration" ], "type": "object" }, "links": [ { "href": "localhost:5000/things/lamp/actions/fade", "rel": "action" } ], "title": "Fade" } }, "description": "A web connected lamp", "events": { "overheated": { "description": "The lamp has exceeded its safe operating temperature", "links": [ { "href": "localhost:5000/things/lamp/events/overheated", "rel": "event" } ], "type": "number", "unit": "degree celsius" } }, "id": "localhost:5000/things/lamp", "links": [ { "href": "localhost:5000/things/lamp/properties", "rel": "properties" }, { "href": "localhost:5000/things/lamp/actions", "rel": "actions" }, { "href": "localhost:5000/things/lamp/events", "rel": "events" } ], "properties": { "brightness": { "@type": "BrightnessProperty", "description": "The level of light from 0-100", "links": [ { "href": "localhost:5000/things/lamp/properties/brightness", "rel": "property" } ], "maximum": 100, "minimum": 0, "title": "Brightness", "type": "integer", "unit": "percent" }, "on": { "@type": "OnOffProperty", "description": "Whether the lamp is turned on", "links": [ { "href": "localhost:5000/things/lamp/properties/on", "rel": "property" } ], "title": "On/Off", "type": "boolean" } }, "title": "My Lamp" } '

thing = Thing.decode(json.loads(txt))

print(thing.as_thing_description())"""