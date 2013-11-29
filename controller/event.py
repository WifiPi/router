import sys
import os
import logging
import cgi
import json
import random
import string
import urllib
import base64
import hashlib
import time
from StringIO import StringIO

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
#from setting import conn

#import nomagic
#import nomagic.auth
#import nomagic.feeds

from controller.base import *
import music

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../template/"))

slides = {}

class EventHandler(BaseHandler):
    def get(self):
        self.render("../template/event/event.html")


class EventAdminHandler(BaseHandler):
    def get(self):
        self.render("../template/event/admin.html")

class EventAdminPreviewHandler(BaseHandler):
    def get(self):
        title = self.get_argument("title", "")
        self.finish(slides.get(title, ""))

    def post(self):
        title = self.get_argument("title", "")
        content = self.get_argument("content", "")
        slides[title] = content
        self.finish({})


class EventPushHandler(BaseHandler):
    listeners = set()
    @tornado.web.asynchronous
    def get(self):
        if self not in self.listeners:
            self.listeners.add(self)

    def on_slide_change(self, data):
        self.finish(data)

    def on_connection_close(self):
        self.listeners.remove(self)

    def post(self):
        data = {"title":""}
        print self.listeners
        for i in self.listeners:
            i.on_slide_change(data)

        EventPushHandler.listeners = set()
