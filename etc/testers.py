import requests

LAT = "43.720664"
LON = "10.408427"

# OPEN WEATHER MAP
API_KEY = "647aa595e78b34e517dad92e1cf5e65c"
api_call = "http://api.openweathermap.org/data/2.5/weather?lat="+LAT+"&lon="+LON+"&appid="+API_KEY+"?"

# WEATHER API
API_KEY = "e5dec06056da4e81be1171342200504"
api_call = "http://api.weatherapi.com/v1/current.json?q="+LAT+","+LON+"&key="+API_KEY

report = requests.get(api_call)
if report.status_code == requests.codes.ok:
    report = report.json()
    temp = report["current"]["feelslike_c"]
    light = (float(report["current"]["vis_km"])/10)*255
    print(report,temp,light)