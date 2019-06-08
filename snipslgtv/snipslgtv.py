# -*-: coding utf-8 -*-

import requests
import json
from pylgtv import WebOsClient
from wakeonlan import wol

class SnipsLGTV:
    def __init__(self, _ip, _mac):
        self.ip = str(_ip)
        self.mac = _mac
        self.client = WebOsClient(self.ip)

    def turn_on(self):
        wol.send_magic_packet(self.mac)
        self.client.power_on()

    def turn_off(self):
        self.client.power_off()

    def open_app(self,app_name):
        self.client.launch_app(app_name)

    def close_app(self):
        self.client.close_app()
