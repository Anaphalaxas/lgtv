# -*-: coding utf-8 -*-

import requests
import json
from pylgtv import WebOsClient
from wakeonlan import send_magic_packet

id_dict = {
    "Netflix":"netflix",
    "Amazon Prime":"amazon",
    "Hulu":"hulu",
    "YouTube":"youtube.leanback.v4"
}

class SnipsLGTV:
    def __init__(self, _ip, _mac):
        self.ip = str(_ip)
        self.mac = _mac
        self.client = WebOsClient(self.ip,"/keys/lg.key")

    def turn_on(self):
        send_magic_packet(self.mac)
        self.client.power_on()

    def turn_off(self):
        print("SNIPSLGTV OFF CALLED: %s" % self.ip)
        self.client.power_off()

    def open_app(self,app_name):
        print("Asked to start %s" % app_name)
        app_id = id_dict[app_name]
        print("Given app_id %s" % app_id)
        self.client.launch_app(app_id)

    def close_app(self):
        self.client.close_app()

    def set_volume(self,volume):
        if volume > 70:
            print("TOO LOUD!")
        else:
            self.client.set_volume(volume)
