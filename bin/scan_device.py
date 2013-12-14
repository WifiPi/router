import sys
import os
import subprocess
import time
import datetime
import socket
import urllib2
import json

import tornado.ioloop

import ping

"""
pipes = {}
mac2ip = {}
ip2mac = {}

def start():
    mac2ip = {}
    ip2mac = {}
    
    #output = subprocess.check_output("nmap -sP 172.31.50.75/23", shell=True)

    p = os.popen("nmap -sP 172.31.50.75/23")
    tornado.ioloop.IOLoop.instance().add_handler(p.fileno(), on_nmap_output, tornado.ioloop.IOLoop.instance().READ)
    pipes[p.fileno()] = p

def on_nmap_output(fd, events):
    #print fd
    output = pipes[fd].read()
    del pipes[fd]
    tornado.ioloop.IOLoop.instance().remove_handler(fd)

    mac = None
    ip = None

    for i in output.split("\n"):
        #print i
        if i.startswith("MAC Address: "):
            mac = i[len("MAC Address: "): len("MAC Address: ")+len("00:1C:10:49:78:E2")]
            #print mac

        if i.startswith("Nmap scan report for "):
            ip = i[len("Nmap scan report for "):]
            #print ip

        if mac and ip and i.startswith("Host is up "):
            mac2ip[mac] = ip
            ip2mac[ip]  = mac

            mac = None
            ip = None

    #print mac2ip
    for mac, ip in mac2ip.iteritems():
        if mac and ip:
            mac2name = conn.get("SELECT * FROM mac2name WHERE mac = %s", mac)

            comment = ""
            if not mac2name:
                output = subprocess.check_output("smbutil status %s" % ip, shell=True)
                if "Server: " in output:
                    comment = output[output.index("Server: ") + len("Server: "):].strip()
                    print comment

            #p = os.popen("ping -c 1 %s" % ip)
            #tornado.ioloop.IOLoop.instance().add_handler(p.fileno(), on_ping, tornado.ioloop.IOLoop.instance().READ)
            #pipes[p.fileno()] = (p, mac2name, mac, ip, comment)

            try:
                rate, _, _ = ping.quiet_ping(ip)
                status = 1 if rate > 50 else 0
            except:
                status = 0
            print ip, status, mac

            if mac2name:
                if mac2name["status"] != status:
                    conn.execute("INSERT INTO status_log (mac, status) VALUES(%s, %s)", mac, status)
                conn.execute("UPDATE mac2name SET ip = %s, comment = %s, status = %s WHERE mac = %s", ip, comment, status, mac)
            else:
                conn.execute("INSERT INTO mac2name (mac, ip, comment, status) VALUES(%s, %s, %s, %s)", mac, ip, comment, status)

    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 15, start)

def on_ping(fd, events):
    print fd
    p, mac2name, mac, ip, comment = pipes[fd]
    output = p.read()
    del pipes[fd]
    tornado.ioloop.IOLoop.instance().remove_handler(fd)

    #print "0.0% packet loss" in output
    if "0.0% packet loss" in output:
        status = 1
    else:
        status = 0
    print ip, status

    if mac2name:
        if mac2name["status"] != status:
            conn.execute("INSERT INTO status_log (mac, status) VALUES(%s, %s)", mac, status)
        conn.execute("UPDATE mac2name SET ip = %s, comment = %s, status = %s WHERE mac = %s", ip, comment, status, mac)
    else:
        conn.execute("INSERT INTO mac2name (mac, ip, comment, status) VALUES(%s, %s, %s, %s)", mac, ip, comment, status)

    #print ip2mac
"""

def main():
    f1 = open("/var/www/router/wifi_ping.log", "a+")
    period = [0] * 200
    on = False
    while True:
        """
        try:
            result = socket.getaddrinfo("KJs-iPhone.local",None)
            print result
            ip = result[0][4][0]
        except:
            pass
        """
        req = urllib2.urlopen("http://127.0.0.1/api/device/monitor")
        json_data = req.read()
        heartbeat = 0
        for ip in json.loads(json_data):
            if ping.do_one(ip, 2, 64):
                print >> f1, datetime.datetime.now().isoformat(), "ON", ip
                heartbeat = 1
            else:
                print >> f1, datetime.datetime.now().isoformat(), "OFF", ip
        f1.flush()

        period.append(heartbeat)
        if len(period) > 200:
            period.pop(0)
        print sum(period), period

        if sum(period) > 1:
            if on is False:
                urllib2.urlopen("http://127.0.0.1/api/play")
                on = True
        else:
            if on is True:
                urllib2.urlopen("http://127.0.0.1/api/stop")
                on = False

        time.sleep(3)


if __name__ == "__main__":
    main()
