#!/usr/bin/env python

import sys
import os
import urllib
import urllib2
import datetime

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../vendor')

#os.chdir(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    with open(os.path.dirname(os.path.abspath(__file__)) + "/../dhcp_hook.log", "a+") as f:
        print >> f, datetime.datetime.now().isoformat(), sys.argv[1:]

    #urllib2.urlopen("http://127.0.0.1/api/play")

    data = {
        "mac": sys.argv[2],
        "ipv4": sys.argv[3],
    }
    if len(sys.argv) > 4:
    	data["name"] = sys.argv[4]

    urllib2.urlopen("http://127.0.0.1/api/device/add", urllib.urlencode(data))
