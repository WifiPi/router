import sys
import os
import subprocess
import time
import datetime
import socket
import urllib2
import json

#import tornado.ioloop
#import tornado.database

try:
    import RPi.GPIO as GPIO
except:
    GPIO = None

if GPIO:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)

sdx = {11:{}, 12:{}, 15:{}, 16:{}}

def scan_port(board_io_port):
    global sdx
    if GPIO:
        GPIO.output(board_io_port, False)
        time.sleep(2)
        try:
            existing_devices = set(subprocess.check_output("ls /dev/sd*", shell=True).split())
        except:
            existing_devices = set()

        GPIO.output(board_io_port, True)
        time.sleep(2)

        try:
            current_devices = set(subprocess.check_output("ls /dev/sd*", shell=True).split())
        except:
            current_devices = set()

        new_devices = current_devices - existing_devices
        print "new devices:"
        print new_devices

        if len(new_devices) == 0:
            pass
            #there was no device on this port
        elif len(new_devices) == 1:
            pass
        elif len(new_devices) > 1:
            pass
        sdx[board_io_port] = {}

        GPIO.output(board_io_port, False)
        time.sleep(2)

if __name__ == "__main__":
    #scan_port(11)
    pass

"""
GPIO.output(11, False)
GPIO.output(12, False)
GPIO.output(15, False)
GPIO.output(16, False)

GPIO.output(11, True)
time.sleep(2)
GPIO.output(11, False)
time.sleep(1)

GPIO.output(12, True)
time.sleep(2)
GPIO.output(12, False)
time.sleep(1)

GPIO.output(15, True)
time.sleep(2)
GPIO.output(15, False)
time.sleep(1)

GPIO.output(16, True)
time.sleep(2)
GPIO.output(16, False)
time.sleep(1)
"""
