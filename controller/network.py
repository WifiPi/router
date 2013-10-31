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

def setup(settings):
    assert 'wan' in settings
    if settings['wan'] == 'pppoe':
        assert 'pppoe_username' in settings
        assert 'pppoe_password' in settings
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

    assert 'ssid' in settings
    assert 'ssid_password' in settings
    assert 'router_ip' in settings
    assert 'router_mask' in settings
    assert 'dhcp_range_start' in settings
    assert 'dhcp_range_end' in settings

    root_path = os.path.dirname(os.path.abspath(__file__)) + '/../'
    # or root_path = '/'
    print root_path

    #hostapd
    with open(root_path + "etc/hostapd/hostapd.conf", "w") as f:
        print >> f, loader.load("etc/hostapd/hostapd.conf").generate(**settings)

    #dnsmasq
    with open(root_path + "etc/dnsmasq.conf", "w") as f:
        print >> f, loader.load("etc/dnsmasq.conf").generate(**settings)

    #network interface
    with open(root_path + "etc/network/interfaces", "w") as f:
        print >> f, loader.load("etc/network/interfaces").generate(**settings)

    #ignore sysctl.conf

    #reinstall watch-wlan0
    with open(root_path + "etc/init.d/watch-wlan0", "w") as f:
        print >> f, loader.load("etc/init.d/watch-wlan0").generate(**settings)


class NetworkHandler(BaseHandler):
    def get(self):
        self.render("../template/network.html")

class NetworkChangeAPIHandler(BaseHandler):
    def get(self):
        setup({
            'wan': 'pppoe',
            'pppoe_username': '',
            'pppoe_password': '',
            'ssid': 'LongPlay',
            'ssid_password': 'raspberry',
            'router_ip': '192.168.10.1',
            'router_mask': '255.255.255.0',
            'dhcp_range_start': '192.168.10.2',
            'dhcp_range_end': '192.168.10.254',
        })
