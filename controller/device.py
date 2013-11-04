import sys
import os
import logging
import cgi
import json
import random
import string
import urllib

import tornado.options
import tornado.ioloop
import tornado.web

import tornado.template
import tornado.database
import tornado.auth
import tornado.locale

#import markdown2
from tornado_ses import EmailHandler
#from amazon_ses import EmailMessage

from setting import settings
from setting import conn

#import nomagic
#import nomagic.auth
#import nomagic.feeds

from controller.base import *
import music

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../template/"))

devices = {}
monitored_devices = {}
def get_devices():
    for result in conn.query("SELECT * FROM device_log"):
        devices[result['ipv4']] = result['name'], result['mac']
    for result in conn.query("SELECT * FROM device_monitor"):
        monitored_devices[result['ipv4']] = result['name']
get_devices()

class DeviceHandler(BaseHandler):
    def get(self):
        get_devices()
        self.devices = devices
        self.render("../template/device.html")

class DeviceAddAPIHandler(BaseHandler):
    def get(self):
        mac = "00:00:00:00:00:00"
        ipv4 = "192.168.10.1"
        name = "WifiPi Router"
        conn.execute("INSERT INTO device_log (ipv4, mac, name) VALUES (%s, %s, %s)", ipv4, mac, name)
        devices[ipv4] = name

    def post(self):
        mac = self.get_argument("mac")
        ipv4 = self.get_argument("ipv4")
        name = self.get_argument("name")
        conn.execute("INSERT INTO device_log (ipv4, mac, name) VALUES (%s, %s, %s)", ipv4, mac, name)
        devices[ipv4] = name

class DeviceMonitorAPIHandler(BaseHandler):
    """
    return devices' ip which need to monitor by ping
    """
    def get(self):
        self.finish(monitored_devices)
