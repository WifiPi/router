import sys
import os
import logging
import cgi
import json
import random
import string
import urllib
import time

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

#import nomagic
#import nomagic.auth
#import nomagic.feeds

from controller.base import *

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../template/"))


"""
cp etc/ppp/peers/dsl-provider /etc/ppp/peers/
cp etc/ppp/pap-secrets /etc/ppp/
pon dsl-provider

#cp etc/default/hostapd /etc/default/
cp etc/hostapd/hostapd.conf /etc/hostapd/

cp etc/dnsmasq.conf /etc/
#cp etc/dhcp/dhclient.conf /etc/dhcp/

cp etc/network/interfaces /etc/network/
#cp etc/network/if-pre-up.d/iptables /etc/network/if-pre-up.d/
#cp etc/iptables.up.rules /etc/
chmod +x /etc/network/if-pre-up.d/iptables

#cp etc/supervisor/conf.d/router.conf /etc/supervisor/conf.d/
#supervisorctl reload

#cp etc/sysctl.conf /etc/
#echo "1" > /proc/sys/net/ipv4/ip_forward

cp etc/init.d/watch-wlan0 /etc/init.d/
chmod +x /etc/init.d/watch-wlan0
update-rc.d watch-wlan0 defaults


/etc/init.d/networking restart
/etc/init.d/hostapd restart
/etc/init.d/dnsmasq restart
#/etc/init.d/watch-wlan0 restart
## or
#reboot
"""

root_path = os.path.dirname(os.path.abspath(__file__)) + '/../'
root_path = '/'

def save(settings):
    assert 'wan' in settings
    if settings['wan'] == 'pppoe':
        assert 'pppoe_username' in settings
        assert 'pppoe_password' in settings

        with open(root_path + "etc/ppp/peers/dsl-provider", "w") as f:
            print >> f, loader.load("etc/ppp/peers/dsl-provider").generate(**settings)

        with open(root_path + "etc/ppp/pap-secrets", "w") as f:
            print >> f, loader.load("etc/ppp/pap-secrets").generate(**settings)

    elif settings['wan'] == 'dhcp':
        pass
    elif settings['wan'] == 'static':
        pass
    #else if settings['wan'] == 'client':
        # not config as an AP
        # both wireless and wired are dhcp
        # need wifi and password
        # wired connection needed
        #assert 'ssid' in settings
        #return

    assert 'wifi_mode' in settings
    assert 'ssid' in settings
    assert 'ssid_password' in settings
    assert 'router_ip' in settings
    assert 'router_mask' in settings
    assert 'dhcp_range_start' in settings
    assert 'dhcp_range_end' in settings
    assert 'secure' in settings

    #hostapd
    with open("%setc/hostapd/hostapd.conf" % root_path, "w") as f:
        print >> f, loader.load("etc/hostapd/hostapd.conf").generate(**settings)

    #dnsmasq
    with open("%setc/dnsmasq.conf" % root_path, "w") as f:
        print >> f, loader.load("etc/dnsmasq.conf").generate(**settings)

    #network interface
    with open("%setc/network/interfaces" % root_path, "w") as f:
        print >> f, loader.load("etc/network/interfaces").generate(**settings)

    #ignore sysctl.conf

    #reinstall watch-wlan0
    with open("%setc/init.d/watch-wlan0" % root_path, "w") as f:
        print >> f, loader.load("etc/init.d/watch-wlan0").generate(**settings)

def load():
    result = {
        "wifi_mode": "create",
        "wan": "dhcp",
        "router_ip": "10.0.0.1",
        "router_mask": "255.255.0.0"
    }
    with open("%setc/hostapd/hostapd.conf" % root_path, "r") as f:
        for i in f.readlines():
            if i.startswith("ssid="):
                line = i.strip()
                result["ssid"] = line[len("ssid="):]

            elif i.startswith("wpa_passphrase="):
                line = i.strip()
                result["ssid_password"] = line[len("wpa_passphrase="):]

        if result.get("ssid_password"):
            result["secure"] = "wpa2"
        else:
            result["secure"] = "none"
            result["ssid_password"] = ""

    with open("%setc/dnsmasq.conf" % root_path, "r") as f:
        for i in f.readlines():
            if i.startswith("ssid="):
                line = i.strip()
                result["ssid"] = line[len("ssid="):]

    with open("%setc/network/interfaces" % root_path, "r") as f:
        for i in f.readlines():
            if i.startswith("address "):
                line = i.strip()
                result["router_ip"] = line[len("address "):]

            elif i.startswith("netmask "):
                line = i.strip()
                result["router_mask"] = line[len("netmask "):]

            elif i.startswith("auto dsl-provider"):
                result["wan"] = "pppoe"

            elif i.startswith("wpa-ssid"):
                result["wifi_mode"] = "join"

    with open("%setc/ppp/peers/dsl-provider" % root_path, "r") as f1:
        for i in f1.readlines():
            if i.startswith("user "):
                result["pppoe_username"] = i.strip()[len("user "):].strip('"')

                with open("%setc/ppp/pap-secrets" % root_path, "r") as f2:
                    for i in f2.readlines():
                        if i.startswith('"%s"' % result["pppoe_username"]):
                            result["pppoe_password"] = i.strip()[len('"%s" * ' % result["pppoe_username"]):].strip('"')

    ip_segments = result["router_ip"].split(".")
    if ip_segments[0] == "192":
        ip_segments[3] = "2"
        result["dhcp_range_start"] = ".".join(ip_segments)
        ip_segments[3] = "255"
        result["dhcp_range_end"] = ".".join(ip_segments)

    elif ip_segments[0] == "10":
        ip_segments[2], ip_segments[3] = "0","2"
        result["dhcp_range_start"] = ".".join(ip_segments)
        ip_segments[2], ip_segments[3] = "255","255"
        result["dhcp_range_end"] = ".".join(ip_segments)

    #with open(root_path + "etc/init.d/watch-wlan0", "r") as f:
    #    pass

    return result

class NetworkHandler(BaseHandler):
    def get(self):
        if not self.current_user or (time.time() - self.current_user["time"]) > 300:
            self.redirect("/login")
            return

        settings = load()
        self.render("../template/network.html", **settings)

class NetworkChangeAPIHandler(BaseHandler):
    def get(self):
        if not self.current_user or (time.time() - self.current_user["time"]) > 300:
            self.redirect("/login")
            return

        save({
            'wifi_mode': 'create',
            'ssid': 'LongPlay',
            'ssid_password': 'raspberry',
            'secure': 'wpa2',

            'wan': 'pppoe',
            'pppoe_username': '',
            'pppoe_password': '',

            'router_ip': '192.168.1.1',
            'router_mask': '255.255.255.0',
            'dhcp_range_start': '192.168.1.2',
            'dhcp_range_end': '192.168.1.254',
        })

        self.finish(load())

class NetworkWifiAPIHandler(BaseHandler):
    def post(self):
        if not self.current_user or (time.time() - self.current_user["time"]) > 300:
            self.redirect("/login")
            return

        settings = load()
        secure = self.get_argument("secure")
        settings['secure'] = secure
        settings['wifi_mode'] = self.get_argument("wifi_mode")
        settings['ssid'] = self.get_argument("ssid")

        if secure == "wpa2":
            ssid_password = self.get_argument("ssid_password", "")
            if len(ssid_password) < 8:
                self.finish({"error": "password length must longer than 8 characters."})
                return
            settings["ssid_password"] = ssid_password

        save(settings)
        self.finish({})

        if settings['wifi_mode'] == "join":
            os.system("update-rc.d watch-wlan0 disable 2")
            os.system("update-rc.d dnsmasq disable 2")
            os.system("update-rc.d hostapd disable 2")

            os.system("/etc/init.d/hostapd stop")
            os.system("/etc/init.d/dnsmasq stop")
            os.system("/etc/init.d/networking restart")
        else:
            os.system("update-rc.d watch-wlan0 enable 2")
            os.system("update-rc.d dnsmasq enable 2")
            os.system("update-rc.d hostapd enable 2")

            os.system("/etc/init.d/hostapd restart")
            os.system("/etc/init.d/watch-wlan0")

class NetworkWanAPIHandler(BaseHandler):
    def post(self):
        if not self.current_user or (time.time() - self.current_user["time"]) > 300:
            self.redirect("/login")
            return

        settings = load()

        wan = self.get_argument("wan")
        settings["wan"] = wan
        if wan == "pppoe":
            settings["pppoe_username"] = self.get_argument("pppoe_username")
            settings["pppoe_password"] = self.get_argument("pppoe_password")

        save(settings)
        os.system("/usr/bin/poff -a")
        if wan == "pppoe":
            os.system("/usr/bin/pon dsl-provider")
        self.finish({})

class NetworkLanAPIHandler(BaseHandler):
    def post(self):
        if not self.current_user or (time.time() - self.current_user["time"]) > 300:
            self.redirect("/login")
            return

        settings = load()
        router_ip = self.get_argument("router_ip")
        settings['router_ip'] = router_ip

        ip_segments = router_ip.split(".")
        if ip_segments[0] == "192":
            settings['router_mask'] = '255.255.255.0'
            ip_segments[3] = "2"
            settings["dhcp_range_start"] = ".".join(ip_segments)
            ip_segments[3] = "255"
            settings["dhcp_range_end"] = ".".join(ip_segments)

        elif ip_segments[0] == "10":
            settings['router_mask'] = '255.255.0.0'
            ip_segments[2], ip_segments[3] = "0","2"
            settings["dhcp_range_start"] = ".".join(ip_segments)
            ip_segments[2], ip_segments[3] = "255","255"
            settings["dhcp_range_end"] = ".".join(ip_segments)

        save(settings)
        self.finish({})
        os.system("/etc/init.d/networking restart")
        os.system("/etc/init.d/watch-wlan0")
