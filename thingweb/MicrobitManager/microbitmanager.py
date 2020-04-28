import requests

uri = "http://131.114.73.148:2000/"

r = requests.get(uri)
print(r.status_code,r.text,r.json())

r = requests.get(uri+"/tetoz")
print(r.status_code,r.text,r.json())

r = requests.patch(uri+"/tetoz/properties/serial_number",json={42})
print(r.status_code,r.text,r.json())

r = requests.patch(uri+"/tetoz/properties/temp",json={42})
print(r.status_code,r.text,r.json())