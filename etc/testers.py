import requests


LAT = "43.720664"
LON = "10.408427"

# WEATHER API (10.000 calls/month)
# MORE INFO per Call
# FEEL LIKE TEMP WRONG?
def call_weatherapi():
    API_KEY = "e5dec06056da4e81be1171342200504"
    api_call = "http://api.weatherapi.com/v1/current.json?q="+LAT+","+LON+"&key="+API_KEY
    report = requests.get(api_call)
    if report.status_code == requests.codes.ok:
        report = report.json()
        print(report)
        temp = report["current"]["temp_c"]
        light = (float(report["current"]["uv"])/11)*255 # uv index max 11
        return True,temp,light
    return False,None,None

# OPEN WEATHER MAP (60 calls/min) (30 because two cal for request: weather and uv)
# or 1.000/day with one call api
# MORE PRECISE
def call_openweathermap():
    API_KEY = "647aa595e78b34e517dad92e1cf5e65c"
    api_call_temp = "http://api.openweathermap.org/data/2.5/weather?units=metric&lat="+LAT+"&lon="+LON+"&appid="+API_KEY
    api_call_uvi = "http://api.openweathermap.org/data/2.5/uvi?lat="+LAT+"&lon="+LON+"&appid="+API_KEY
    report_temp = requests.get(api_call_temp)
    report_uvi = requests.get(api_call_uvi)
    if report_temp.status_code == requests.codes.ok or report_uvi.status_code == requests.codes.ok:
        temp = None
        light = None
        if report_temp.status_code == requests.codes.ok:
            report_temp = report_temp.json()
            print(report_temp)
            temp = report_temp["main"]["temp"]
        if report_uvi.status_code == requests.codes.ok:
            report_uvi = report_uvi.json()
            print(report_uvi)
            light = (float(report_uvi["value"])/11)*255 # uv index max 11
        return True,temp,light

    return False,None,None


print(call_weatherapi())
print(call_openweathermap())
