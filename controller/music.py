
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import subprocess
import time
import os
import random

import tornado.ioloop
from tornado.ioloop import IOLoop
try:
    import RPi.GPIO as GPIO
except:
    GPIO = None

if GPIO:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(18, GPIO.OUT)

p = None # the process of mpg123
s = None # schedule of turn off the speaker power
w = None # watch if the process ends, and play the next song

def play(filename):
    #print filename
    global p
    stop()
    p = subprocess.Popen(["mpg123", filename]) #mpg123
    turn_on()

    global w
    if w:
        w.stop()
    w = tornado.ioloop.PeriodicCallback(watch, 5*1000)
    w.start()

def stop():
    global p
    if p:
        p.terminate()
        p = None
        turn_off_in(10)

    global w
    if w:
        w.stop()


def turn_on():
    global s
    if s:
        #cancel turn off schedule if there is
        IOLoop.instance().remove_timeout(s)
        s = None

    if GPIO:
        GPIO.output(18, True)

def turn_off_in(seconds):
    global s
    if s:
        #cancel turn off schedule if there is
        IOLoop.instance().remove_timeout(s)
        s = None

    def turn_off():
        if GPIO:
            GPIO.output(18, False)

    s = IOLoop.instance().add_timeout(time.time() + seconds, turn_off)

def watch():
    global p
    if p:
        print "CHECK", p.poll(), p.returncode
        if p.poll() is not None:
            p = None
            random_song()


def random_song():
    mp3s = [i for i in os.listdir(os.path.dirname(os.path.abspath(__file__)) + "/../mp3/") if i.endswith(".mp3")]
    play(os.path.dirname(os.path.abspath(__file__)) + "/../mp3/"+random.choice(mp3s))


if __name__ == '__main__':
    random_song()
    IOLoop.instance().start()
    time.sleep(10)
    #stop()
