#!/usr/bin/env python

import sys
import os
import urllib2
#import logging
#import cgi

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/vendor')

#os.chdir(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    with open("/home/pi/testing/dhcp_hook.log", "a+") as f:
        print >> f, sys.argv[1:]
        urllib2.urlopen("http://127.0.0.1/api/play")

