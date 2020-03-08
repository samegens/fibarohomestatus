import cherrypy
import requests
from jinja2 import Template
import datetime
import urllib.parse
import os
 
class Root(object):
    _fibaro_to_name_list = [
        [ "Deursensor 4", "Achterdeur" ],
        [ "Raamsensor 6", "Woonkamerraam" ],
        [ "Raamsensor 7", "Keukenraam" ],
#        [ "Raamsensor 5", "Badkamerraam" ],
        [ "Raamsensor 10", "Badkamerraam" ],
        [ "Raamsensor 3", "Kate slaapkamerraam" ],
        [ "Raamsensor 2", "Ouderslaapkamerraam" ],
#        [ "Raamsensor 1", "Werkkamerraam" ]
        [ "Raamsensor 9", "Werkkamerraam" ]
    ]
    _fibaro_to_name_map = dict(_fibaro_to_name_list)
    _devices_names = [x[0] for x in _fibaro_to_name_list]
    _template = Template('''
    <html>
        <head>
            <meta http-equiv="refresh" content="10">
            <meta name="mobile-web-app-capable" content="yes">
            <title>Huis status</title>
            <style>
                body {
                    background-color: black;
                    color: #e0e0e0;
                    font-family: sans-serif;
                    margin-top: 40px;
                }
                .last-updated {
                    font-size: 200%;
                    margin-bottom: 40px;
                }
                table {
                    font-size: 400%;
                }
                .open {
                    background-color: red;
                    color: black;
                    background-clip: padding-box;
                    border-radius: 15px;
                    padding-left: 25px;
                    padding-right: 25px;
                }
                .closed {
                    background-color: #56d121;
                    color: black;
                    background-clip: padding-box;
                    border-radius: 15px;
                    padding-left: 25px;
                    padding-right: 25px;
                }
            </style>
        </head>
        <body>
            <center>
                <div class="last-updated">Laatste update: {{ now.strftime("%H:%M:%S %d-%m-%Y") }}</div>
                <table>
                        {% for device in devices %}
                            <tr>
                                <td>{{ device.name }}</td><td class="{{'open' if device.is_open else 'closed'}}">{{ 'open' if device.is_open else 'dicht' }}</td>
                            </tr>
                        {% endfor %}
                        <tr>
                            <td style="height: 40px"></td>
                        </tr>
                        <tr>
                            <td colspan="2" style="height: 700px" class="{{'open' if is_anything_open else 'closed'}}"></td>
                        </tr>
                </table>
            </center>
        </body>
    </html>''')

    @cherrypy.expose
    def index(self):
        user_name = urllib.parse.quote(os.getenv("FIBARO_USER_NAME") or "nobody")
        password = urllib.parse.quote(os.getenv("FIBARO_PASSWORD") or "secret")
        host = os.getenv("FIBARO_HOST") or "localhost"
        url = "http://{0}:{1}@{2}/api/devices".format(user_name, password, host)
        r = requests.get(url=url, headers={"X-Fibaro-Version": "2"})
        if r.status_code != 200:
            return "{0}: {1}".format(r.status_code, r.text)

        device_to_result_map = {}
        for device in r.json():
            name = device["name"]
            if name in Root._devices_names:
                nl_name = Root._fibaro_to_name_map[name]
                device_to_result_map[name] = {
                    "name": nl_name,
                    "is_open": device["properties"]["value"]
                }

        device_states = []
        for device_name in Root._devices_names:
            device_states.append(device_to_result_map[device_name])

        is_anything_open = False
        for device_state in device_states:
            if device_state["is_open"]:
                is_anything_open = True
        
        html = Root._template.render(devices = device_states, now = datetime.datetime.now(), is_anything_open = is_anything_open)
        return html

if __name__ == "__main__":
    # Running server.py directly from command line.
    cherrypy.quickstart(Root())
else:
    # Running server.py from cherryd
    cherrypy.tree.mount(Root())
