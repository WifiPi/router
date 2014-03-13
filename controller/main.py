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
import shutil

#import tornado.ioloop
import tornado.web
#import tornado.template
#import tornado.auth
#import tornado.locale

#import markdown2
from tornado_ses import EmailHandler
#from amazon_ses import EmailMessage

from setting import settings
from setting import conn
from setting import conn_remote


from controller.base import *
import music


class MainHandler(BaseHandler):
    def get(self):
        self.redirect("/network")


class LoginHandler(BaseHandler, EmailHandler):
    def get(self):
        self.email = self.get_argument("email", u"")
        self.render('../template/login.html')

    def post(self):
        login = self.get_argument("login")
        password = self.get_argument("password")

        user = conn_remote.get("SELECT * FROM users WHERE login = %s", login)
        if user and user["password"] == hashlib.sha1(password).hexdigest():
            user_id = user["id"]
            self.set_secure_cookie("user", tornado.escape.json_encode({"user_id": user_id, "time": time.time()}))
            self.redirect("/network")
            return

        self.redirect("/login?status=error")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.render("../template/logout.html")


class MusicHandler(BaseHandler):
    def get(self):
        self.render("../template/music.html")

class MessageHandler(BaseHandler):
    def get(self):
        self.render("../template/message.html")


class PlayAPIHandler(BaseHandler):
    def get(self):
        music.random_song()
        self.finish({})

class StopAPIHandler(BaseHandler):
    def get(self):
        music.stop()
        self.finish({})

