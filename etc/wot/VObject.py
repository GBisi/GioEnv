import requests
import json

class MalformedObjectError(Exception):
    pass

class ConnectionError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

def httpRequest(method, url, jsonData = None):

    if method == "GET":
        r = requests.get(url)
    elif method == "POST":
        r = requests.post(url, json=jsonData)
    elif method == "PUT":
        r = requests.put(url, json=jsonData)

    if r.status_code == 200:
        return r.text
    else: 
        raise ConnectionError(r.status_code,r.text)
    

def request_factory(method, url, jsonData = None, name = None):
    if method == "GETJSON" and name is not None:
        return lambda: json.loads(httpRequest("GET",url,jsonData))[name]
    elif method == "GETJSON":
        return lambda: json.loads(httpRequest("GET",url,jsonData))
    return lambda: httpRequest(method,url,jsonData)


class VObject:

    def __init__(self, url):

        text = httpRequest("GET",url)
        desc = json.loads(text)
        
        if "actions" in desc:
            for a, d in desc['actions'].items():
                action = {'name': a}
                for l in d['links']:
                    if l['rel'] == 'action':
                        action['href'] = l['href']
                if 'href' not in action:
                    raise MalformedObjectError
                if 'input' in d:
                    action['f'] = request_factory("POST",action["href"], {action['name']:{"input":inp}})
                else:
                    action['f'] = request_factory("POST",action["href"], {action['name']:{}})
                setattr(self, action['name'], action["f"])


        if "properties" in desc:
            for p, d in desc['properties'].items():
                prop = {'name': p}

                for l in d['links']:
                    if l['rel'] == 'property':
                        prop['href'] = l['href']
                if 'href' not in prop:
                    raise MalformedObjectError

                if 'writeOnly' not in d or not d["writeOnly"]:
                    setattr(self, "get_"+prop["name"], request_factory("GETJSON",prop["href"],name=prop["name"]))

                if 'readOnly' not in d or not d["readOnly"]:
                    setattr(self, "set_"+prop["name"], request_factory("PUT",prop['href'], {prop["name"]:val}))


            if "events" in desc:
                href = None
                for l in desc['links']:
                    if l['rel'] == 'events':
                        href = l["href"]
                        setattr(self, "get_events", request_factory("GETJSON",href))


vo = VObject('http://localhost:4242/things/room329A')
print(vo.get_events())