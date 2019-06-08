#!/usr/bin/env python3
# -*-: coding utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
import hermes_python
import io
import os
import sys
from snipslgtv.snipslgtv import SnipsLGTV

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

DIR = os.path.dirname(os.path.realpath(__file__)) + '/alarm/'

lang = "EN"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name: option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def tvOn(hermes,intent_message):
    print("CHANCE: TVON CALLED")
    res = hermes.skill.turn_on()
    print("CHANCE: POST_TURNON")
    current_session_id = intent_message.session_id
    hermes.publish_end_session(current_session_id, res.decode("latin-1"))

def tvOff(hermes,intent_message):
    res = hermes.skill.turn_off()
    current_session_id = intent_message.session_id
    hermes.publish_end_session(current_session_id, res.decode("latin-1"))

def closeApp(hermes,intent_message):
    res = hermes.skill.close_app()
    current_session_id = intent_message.session_id
    hermes.publish_end_session(current_session_id, res.decode("latin-1"))

def openApp(hermes,intent_message):
    app_name = intent_message.slots.appName
    if not app_name:
        print("Could not read App name from intent message")
    res = hermes.skill.open_app(app_name)
    current_session_id = intent_message.session_id
    hermes.publish_end_session(current_session_id, res.decode("latin-1"))


if __name__ == "__main__":
    config = read_configuration_file(CONFIG_INI)
    ip = config.get("secret", "ip")
    if not ip:
        print("Could not load [secret][ip] from %s" % CONFIG_INI)
        sys.exit(1)
    mac = config.get("secret", "mac")
    if not mac:
        print("Could not load [secret][mac] from %s" % CONFIG_INI)
        sys.exit(1)
    skill = SnipsLGTV(ip, mac)
    with Hermes(MQTT_ADDR) as h:
        h.skill = skill
        h.subscribe_intent("tvOn", tvOn).subscribe_intent("tvOff", tvOff)\
         .subscribe_intent("openApp", openApp).subscribe_intent("closeApp", closeApp)\
         .loop_forever()
