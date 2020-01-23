import websocket
import threading
import time
import json

class Subscriber:

    def __init__(self, server):
        self.server = server
        self.ws = None

    def run(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://"+self.server,
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_close = self.on_close)

        self.ws.on_open = self.on_open
    
        threading.Thread(target=self.ws.run_forever).start()


        print("WebSocket: Started")

    def on_message(self, message):
        print("WebSocket: New Message")
        print(message)
        message = json.loads(message)
        if "messageType" in message:
            if message["messageType"] == "propertyStatus":
                self.on_propertyStatus(message)
            elif message["messageType"] == "actionStatus":
                self.on_actionStatus(message)
            elif message["messageType"] == "event":
                self.on_event(message)
            else:
                self.on_error(message)


    def requestAction(self, action):
        self.ws.send(str({"messageType":"requestAction",
                      "data":{
                          action:{}
                          }
                      }))

    def setProperty(self, property_):
        self.ws.send(str({"messageType":"setProperty",
                      "data":{
                          property_:{}
                          }
                      }))

    def addEventSubscription(self, event):
        self.ws.send(str({"messageType":"addEventSubscription",
                      "data":{
                          event:{}
                          }
                      }))
    

    # OVERRIDABLE

    def on_open(self):
        print("WebSocket: Connected")

    def on_error(self, error):
        print("WebSocket: Error")
        print(error)

    def on_close(self):
        print("WebSocket: Closed")

    # ABSTRACT

    def on_propertyStatus(self, message):
        print(message)

    def on_actionStatus(self, message):
        print(message)
    def on_event(self, message):
        print(message)


if __name__ == '__main__':
    s = Subscriber("localhost:5000/things/tuvov")
    s.run()
    s.requestAction("action")
