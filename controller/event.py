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
from setting import conn

#import nomagic
#import nomagic.auth
#import nomagic.feeds

from controller.base import *
import music

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../template/"))

slides = {}
current_title = ""
editing_title = ""

class EventHandler(BaseHandler):
    def get(self):
        self.body = slides.get(current_title, "")
        self.render("../template/event/event.html")


class EventAdminHandler(BaseHandler):
    def get(self):
        self.render("../template/event/admin.html")

class EventAdminPreviewHandler(BaseHandler):
    def get(self):
        global editing_title
        #title = self.get_argument("title", "")
        self.finish(slides.get(editing_title, ""))

    def post(self):
        global editing_title
        title = self.get_argument("title", "")
        editing_title = title

        content = self.get_argument("content", "")
        slides[title] = content
        self.finish({})


class EventPushAPIHandler(BaseHandler):
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
        global current_title
        title = self.get_argument("title", "")
        if title:
            current_title = title
        else:
            title = current_title

        data = {"title": title}
        print self.listeners
        for i in self.listeners:
            i.on_slide_change(data)

        EventPushAPIHandler.listeners = set()


class EventListAPIHandler(BaseHandler):
    def get(self):
        slides = conn.query("SELECT * FROM event_slide")
        self.finish({"list": [i.title for i in slides]})

class EventLoadAPIHandler(BaseHandler):
    def get(self):
        title = self.get_argument("title", "")
        slide = conn.get("SELECT * FROM event_slide WHERE title = %s", title)
        self.finish({"title": slide.title, "content": slide.content})

class EventSaveAPIHandler(BaseHandler):
    def post(self):
        title = self.get_argument("title", "")
        content = self.get_argument("content", "")
        if conn.get("SELECT * FROM event_slide WHERE title = %s", title):
            conn.execute("UPDATE event_slide SET content = %s WHERE title = %s", content, title)
        else:
            conn.execute("INSERT INTO event_slide (title, content) VALUES (%s, %s)", title, content)
        self.finish({})

class EventDeleteAPIHandler(BaseHandler):
    def post(self):
        title = self.get_argument("title", "")
        conn.execute("DELETE FROM event_slide WHERE title = %s", title)
        self.finish({})
