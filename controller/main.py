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
#from setting import conn

#import nomagic
#import nomagic.auth
#import nomagic.feeds

from controller.base import *
import music

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../template/"))


class LoginHandler(BaseHandler, EmailHandler):
    def get(self):
        self.email = self.get_argument("email", u"")
        self.invite_code = self.get_argument("invite_code", u"")
        self.render('../template/login.html')

    def post(self):
        login = self.get_argument("login", None)
        password = self.get_argument("password", None)

        invite_code = self.get_argument("invite_code", None)
        email = self.get_argument("email", None)
        name = self.get_argument("name", None)
        password1 = self.get_argument("password1", None)
        password2 = self.get_argument("password2", None)

        if login and password:
            user_id, user = nomagic.auth.check_user(login, password)
            if user_id:
                self.set_secure_cookie("user", tornado.escape.json_encode({"user_id": user_id}))
                self.redirect("/?status=login")
                return

        elif email and name and password1 and password2 and password1 == password2 and invite_code:
            invited = conn.get("SELECT * FROM invite WHERE code = %s", invite_code)
            if not invited:
                self.redirect("/login?status=need_invite_code")
                return

            data = {"email": email, "name": name, "password": password1}
            try:
                user_id, user = nomagic.auth.create_user(data)

                self.set_secure_cookie("user", tornado.escape.json_encode({"user_id": user_id}))

                email_verify_code = ''.join(random.choice(string.digits+string.letters) for x in range(14))
                result = nomagic.auth.update_user(user_id, {"email_verified": False, "email_verify_code": email_verify_code})

                #send verify email here
                msg = EmailMessage()
                msg.subject = "Confirm Email from Pythonic Info"
                msg.bodyText = "http://pythonic.info/verify_email?user_id=%s&verify_code=%s" % (user_id, email_verify_code)
                self.send("info@pythonic.info", str(email), msg)
                print "url:", msg.bodyText

                self.redirect("/?status=created")
                return
            except:
                pass

        self.redirect("/login?status=error")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.render("../template/logout.html")


class MainHandler(BaseHandler):
    def get(self):
        self.render("../template/main.html")

class PlayAPIHandler(BaseHandler):
    def get(self):
        music.play("15bce0a605beaa38e669f026d5697a5e.mp3")
        self.finish({})

class StopAPIHandler(BaseHandler):
    def get(self):
        music.stop()
        self.finish({})

