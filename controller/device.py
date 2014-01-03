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
import tornado.auth
import tornado.locale

#import markdown2
from tornado_ses import EmailHandler
#from amazon_ses import EmailMessage

from setting import settings
from setting import conn
from setting import conn_remote

#import nomagic
#import nomagic.auth
#import nomagic.feeds

from controller.base import *


root_path = os.path.dirname(os.path.abspath(__file__)) + '/../'
root_path = '/'


def get_ip_range():
    with open(root_path + "etc/network/interfaces", "r") as f:
        for i in f.readlines():
            if i.startswith("address "):
                line = i.strip()
                router_ip = line[len("address "):]

            #elif i.startswith("netmask "):
            #    line = i.strip()
            #    router_mask = line[len("netmask "):]

        ip_segments = router_ip.split(".")
        if ip_segments[0] == "192":
            ip_range = "192.168.%s." % ip_segments[2]
        elif ip_segments[0] == "10":
            ip_range = "10.%s." % ip_segments[1]
        else:
            ip_range = None
        return ip_range

devices = {}
monitored_devices = {}
def get_devices():
    ip_range = get_ip_range()
    for result in conn.query("SELECT * FROM device_log"):
        if result['ipv4'].startswith(ip_range):
            devices[result['ipv4']] = result['name'], result['mac']
    for result in conn.query("SELECT * FROM device_monitor"):
        monitored_devices[result['ipv4']] = result['name']

class DeviceHandler(BaseHandler):
    def get(self):
        get_devices()
        self.devices = devices
        self.render("../template/device.html")

class DeviceAddAPIHandler(BaseHandler):
    def get(self):
        mac = "00:00:00:00:00:00"
        ipv4 = "10.0.0.1"
        name = "WifiPi Router"
        conn.execute("INSERT INTO device_log (ipv4, mac, name) VALUES (%s, %s, %s)", ipv4, mac, name)
        devices[ipv4] = name

    def post(self):
        mac = self.get_argument("mac")
        ipv4 = self.get_argument("ipv4")
        name = self.get_argument("name", "")
        conn.execute("INSERT INTO device_log (ipv4, mac, name) VALUES (%s, %s, %s)", ipv4, mac, name)
        devices[ipv4] = name

class DeviceMonitorAPIHandler(BaseHandler):
    """
    return devices' ip which need to monitor by ping
    """
    def get(self):
        get_devices()
        self.finish(monitored_devices)


class PingHandler(BaseHandler):
    def get(self):
        #/wifi/ping/?gw_id=0C8268174423&sys_uptime=70294&sys_memfree=359624&sys_load=0.02&wifidog_uptime=1682
        self.get_argument("gw_id")
        self.get_argument("sys_uptime")
        self.get_argument("sys_memfree")
        self.get_argument("sys_load")
        self.get_argument("wifidog_uptime")
        self.finish("Pong")

class LoginHandler(BaseHandler):
    def get(self):
        #/wifi/login/?gw_address=10.0.0.1&gw_port=2060&gw_id=0C8268174423&url=http%3A//init-p01st.push.apple.com/bag
        #gw_address = self.get_argument("gw_address")
        #gw_port = self.get_argument("gw_port")
        #gw_id = self.get_argument("gw_id")
        #url = self.get_argument("url")

        # find mac by ip?
        remote_ip = self.request.remote_ip if self.request.remote_ip != '127.0.0.1' else self.request.headers['X-Forwarded-For']
        device_logs = conn.query("SELECT * FROM device_log WHERE ipv4 = %s ORDER BY id DESC", remote_ip)
        if len(device_logs) == 0:
            self.finish("Something wrong!")
            return
        mac = device_logs[0]["mac"]

        # find email by mac?
        reg = conn_remote.get("SELECT * FROM event_reg_mac WHERE mac = %s", mac)
        if reg:
            self.redirect("http://10.0.0.1:2060/wifidog/auth?token=%s" % mac)
            return

        self.render("../template/wifi/login.html")

    def post(self):
        email = self.get_argument("email")
        """
        reg = conn_remote.get("SELECT * FROM event_reg WHERE email = %s", email)
        if not reg:
            self.finish("You email is not registered.")
            return
        """

        regs = conn_remote.query("SELECT * FROM event_reg_mac WHERE email = %s", email)
        if len(regs) >= 2:
            self.finish("Sorry, your email has been used for too many times")
            return

        # find mac by ip?
        remote_ip = self.request.remote_ip if self.request.remote_ip != '127.0.0.1' else self.request.headers['X-Forwarded-For']
        device_logs = conn.query("SELECT * FROM device_log WHERE ipv4 = %s ORDER BY id DESC", remote_ip)
        if len(device_logs) == 0:
            self.finish("Something wrong!")
            return
        mac = device_logs[0]["mac"]

        conn_remote.execute("INSERT INTO event_reg_mac (email, mac) VALUES(%s, %s)", email, mac)

        # create an unquie token in database
        self.redirect("http://10.0.0.1:2060/wifidog/auth?token=%s" % mac)

class AuthHandler(BaseHandler):
    def get(self):
        # find the mac address, user ip by token
        #/wifi/auth/?stage=login&ip=10.0.0.18&mac=84:38:35:52:ea:08&token=1234&incoming=0&outgoing=0&gw_id=0810781EE54D
        mac = self.get_argument("mac")

        reg = conn_remote.query("SELECT * FROM event_reg_mac WHERE mac = %s", mac)
        if reg:
            self.finish("Auth: 1") #success
            return

        self.finish("Auth: 0")

class PortalHandler(BaseHandler):
    def get(self):
        self.redirect("/")
        #self.finish("Welcome")

class GWMessageHandler(BaseHandler):
    def get(self):
        #http://10.0.0.1/wifi/gw_message.php?message=denied
        self.finish("Sorry")

class AppleTestHandler(BaseHandler):
    def get(self):
        self.finish("WifiPi Welcome")
