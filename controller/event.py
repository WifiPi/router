import sys
import os
import os.path
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
import tornado.auth
import tornado.locale
import tornado.httpclient

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


slides = {}
current_title = ""
editing_title = ""

class EventHandler(BaseHandler):
    def get(self):
        self.body = slides.get(current_title, "")
        self.render("../template/event/event.html")


class EventAdminHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return

        self.render("../template/event/admin.html")


class EventAdminPreviewHandler(BaseHandler):
    def get(self):
        global editing_title
        #title = self.get_argument("title", "")
        self.finish(slides.get(editing_title, ""))

    def post(self):
        if not self.current_user:
            return

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
        if not self.current_user:
            return

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
        self.finish({})

        clients_json_filename = os.path.join(os.path.dirname(__file__), "../clients.json")
        if not os.path.exists(clients_json_filename):
            return
        cookie = self.request.headers["Cookie"]
        with open(clients_json_filename, "r") as f:
            for ip in json.loads(f.read())["clients"]:
                http = tornado.httpclient.AsyncHTTPClient()
                http.fetch("http://%s/api/event/slide/push" % ip, self._on_fetch, method="POST", headers={"Cookie":cookie}, body="title=%s" % urllib.quote(title))

    def _on_fetch(self, response):
        print response.body
        pass


class EventListAPIHandler(BaseHandler):
    def get(self):
        slides = conn_remote.query("SELECT * FROM event_slide")
        self.finish({"list": [i.title for i in slides]})

class EventLoadAPIHandler(BaseHandler):
    def get(self):
        title = self.get_argument("title", "")
        slide = conn_remote.get("SELECT * FROM event_slide WHERE title = %s", title)
        self.finish({"title": slide.title, "content": slide.content})

class EventSaveAPIHandler(BaseHandler):
    def post(self):
        title = self.get_argument("title", "")
        content = self.get_argument("content", "")
        if conn_remote.get("SELECT * FROM event_slide WHERE title = %s", title):
            conn_remote.execute("UPDATE event_slide SET content = %s WHERE title = %s", content, title)
        else:
            conn_remote.execute("INSERT INTO event_slide (title, content) VALUES (%s, %s)", title, content)
        self.finish({})

class EventDeleteAPIHandler(BaseHandler):
    def post(self):
        title = self.get_argument("title", "")
        conn_remote.execute("DELETE FROM event_slide WHERE title = %s", title)
        self.finish({})
