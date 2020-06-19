from flask import Flask, jsonify, request, abort
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from datetime import datetime
import uuid
import requests
import json
import configparser

IP = "127.0.0.1"
PORT = 8080

S2M = "http://131.114.73.148:2048/"

server = Flask(__name__)
old_dash = []

@server.route("/devices/<device>/<prop>", methods=["PATCH"])
def patch_device(device, prop):
    data = str(datetime.now())+" "+json.dumps(request.json)+"\n"
    r = requests.patch(S2M+device+"/"+prop, data)
    if r.status_code == 200:
        return jsonify(r.json()),200
    else:
        requests.post(S2M+device)
        requests.post(S2M+device+"/"+prop)
        r = requests.patch(S2M+device+"/"+prop, data)
        if r.status_code == 200:
            return jsonify(r.json()),200
    abort(500)

@server.route("/devices/<device>", methods=["GET"])
def get_device(device):
    r = requests.get(S2M+device)
    if r.status_code == 200:
        return jsonify(r.json()), r.status_code
    else:
        abort(r.status_code)

@server.route("/devices/<device>/<prop>", methods=["GET"])
def get_prop(device,prop):
    r = requests.get(S2M+device+"/"+prop)
    if r.status_code == 200:
        return jsonify(r.json()), r.status_code
    else:
        abort(r.status_code)

@server.route("/dashboards", methods=["GET"])
def get_dashboards():
    return jsonify(old_dash)

def get_prop_layout(device, prop):
    
    layout = []

    r = requests.get(S2M+device+"/"+prop)
    if r.status_code == 200:
        x = []
        y = []
        data = r.json()["data"].split("\n")
        for r in data:
            t = r.split(" ")
            if len(t) == 3:
                x.append(t[1])
                y.append(float(t[2]))

        if prop == "temp" or prop == "temperature":
            layout.append(
                html.Div(
                    daq.Thermometer(
                        id=device+"-"+prop+":thermometer",
                        min=-10,
                        max=float(max(y))+5,
                        value=float(y[-1]),
                        showCurrentValue=True,
                        label='Current temperature',
                    ), style={'display': 'inline-block', "width":"15%", "vertical-align": "bottom"},
                )
            )
        else:            
            layout.append(
                html.Div(
                    daq.Gauge(
                        id=device+"-"+prop+":gauge",
                        min=0,
                        max=float(max(y))+5,
                        value=float(y[-1]),
                        showCurrentValue=True,
                        label='Current value'
                    ), style={'display': 'inline-block', "width":"15%", "vertical-align": "bottom"},
                ) 
            )

        layout.append(
            html.Div(
                dcc.Graph(
                    id=device+"-"+prop+":graph",
                    figure=dict(
                        data=[
                            dict(
                                x=x,
                                y=y,
                                name=prop
                            )
                        ],
                    )   
                ), style={'display': 'inline-block', "width":"85%", "vertical-align": "top"},
            )
        )
    else:
        layout.append(html.H2("Error "+str(r.status_code)))
        layout.append(html.H3("Please, try again later"))

    return layout

@server.route("/dash/<device>", methods=["GET"])
def get_device_dashboard(device):
    path = '/dash-'+str(uuid.uuid4())+"/"
    app = Dash(__name__,
               server=server,
               url_base_pathname=path)

    old_dash.append({"timestamp":datetime.now(),"href":"http://"+IP+":"+str(PORT)+path,"device":device})

    layout = [html.H1(device.upper()+" Dashboard")]

    r = requests.get(S2M+device)
    if r.status_code == 200:
        objs = r.json()["objects"]
        for o in objs:
            prop = o["id"]
            layout+=[html.H2("Property: "+prop.capitalize(), style={'textAlign': 'center'})]
            layout+=get_prop_layout(device,prop)
    else:
        layout.append(html.H2("Error "+str(r.status_code)))
        layout.append(html.H3("Please, try again later"))

    app.layout = html.Div(children=layout)
    return app.index()

@server.route("/dash/<device>/<prop>", methods=["GET"])
def get_prop_dashboard(device,prop):
    path = '/dash-'+str(uuid.uuid4())+"/"
    app = Dash(__name__,
               server=server,
               url_base_pathname=path)

    old_dash.append({"timestamp":datetime.now(),"href":"http://"+IP+":"+str(PORT)+path,"device":device,"prop":prop})

    layout = [html.H1(device.capitalize()+"'s "+prop.capitalize()+" Dashboard")] + get_prop_layout(device,prop)

    app.layout = html.Div(children=layout)
    return app.index()

def configuration():
    global IP
    global PORT

    config = configparser.ConfigParser()
    config.read('../config.ini')

    test = config["TEST"].getboolean("TEST")

    if test:
        IP = config["TEST"]["MY_IP"]
    else:
        IP = config["DEFAULT"]["MY_IP"]

    PORT = int(config["DASHBOARD"]["PORT"])
    
    

if __name__ == '__main__':
    
    configuration()
    print("DashPy ONLINE @ "+IP+":"+str(PORT))
    server.run(IP,PORT)