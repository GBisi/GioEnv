import requests

MY_IP = "127.0.0.1"
MEDIATOR_PORT = 1999

mediator = "http://"+MY_IP+":"+str(MEDIATOR_PORT)+"/"
r = requests.get(mediator, json={
	"tempL":"VERY_HIGH", 
	"lightL":"HIGH"
})
text = r.text
print(text)