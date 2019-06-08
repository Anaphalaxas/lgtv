#!/usr/bin/env python3
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes
import hermes_python
import io
import os
import sys
from snipslgtv.snipslgtv import SnipsLGTV
from snipshelpers.thread_handler import ThreadHandler
from snipshelpers.config_parser import SnipsConfigParser
import queue

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

DIR = os.path.dirname(os.path.realpath(__file__)) + '/alarm/'

lang = "EN"


class Skill_LGTV:
    def __init__(self):
        config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        ip = config.get("secret").get("ip", None)
        if not ip:
            print("Could not load [secret][ip] from %s" % CONFIG_INI)
            sys.exit(1)
        mac = config.get("secret").get("mac", None)
        if not mac:
            print("Could not load [secret][mac] from %s" % CONFIG_INI)
            sys.exit(1)
        self.snipslgtv = SnipsLGTV(ip, mac)
        self.queue = queue.Queue()
        self.thread_handler = ThreadHandler()
        self.thread_handler.run(target=self.start_blocking)
        self.thread_handler.start_run_loop()

    def start_blocking(self, run_event):
        while run_event.is_set():
            try:
                self.queue.get(False)
            except queue.Empty:
                with Hermes(MQTT_ADDR) as h:
                    h.subscribe_intents(self.callback).start()

    def tvOn(self,hermes,intent_message):
        print("CHANCE: TVON CALLED")
        res = self.snipslgtv.turn_on()
        print("CHANCE: POST_TURNON")
        current_session_id = intent_message.session_id
        self.terminate_feedback(hermes, intent_message)

    def tvOff(self,hermes,intent_message):
        print("CHANCE: TVOFF CALLED")
        res = self.snipslgtv.turn_off()
        current_session_id = intent_message.session_id
        self.terminate_feedback(hermes, intent_message)

    def closeApp(self,hermes,intent_message):
        res = self.snipslgtv.close_app()
        current_session_id = intent_message.session_id
        self.terminate_feedback(hermes, intent_message)


    def openApp(self,hermes,intent_message):
        app_name = intent_message.slots.appName
        if not app_name:
            print("Could not read App name from intent message")
        res = self.snipslgtv.open_app(app_name)
        current_session_id = intent_message.session_id
        self.terminate_feedback(hermes, intent_message)


    def setVolume(self,hermes,intent_message):
        volume = intent_message.slots.volume
        if not volume:
            print("Could not read volume from intent message")
        res = self.snipslgtv.set_volume(int(volume))
        current_session_id = intent_message.session_id
        self.terminate_feedback(hermes, intent_message)


    def callback(self, hermes, intent_message):
        intent_name = intent_message.intent.intent_name
        print("CHANCE CALLBACK: %s" % intent_name)
        if ':' in intent_name:
            intent_name = intent_name.split(":")[1]
            print("CHANCE AFTER: %s" % intent_name)
        if intent_name == 'tvOn':
            print("CHANCE TV ON")
            self.queue.put(self.tvOn(hermes, intent_message))
        if intent_name == 'tvOff':
            print("CHANCE TV OFF")
            self.queue.put(self.tvOff(hermes, intent_message))
        if intent_name == 'openApp':
            print("CHANCE OPEN APP")
            self.queue.put(self.openApp(hermes, intent_message))
        if intent_name == 'setVolume':
            print("CHANCE SET VOLUME")
            self.queue.put(self.setVolume(hermes, intent_message))

    ####    section -> feedback reply // future function
    def terminate_feedback(self, hermes, intent_message, mode='default'):
        if mode == 'default':
            hermes.publish_end_session(intent_message.session_id, "")
        else:
            #### more design
            hermes.publish_end_session(intent_message.session_id, "")


if __name__ == "__main__":
    Skill_LGTV()
