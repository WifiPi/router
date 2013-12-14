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
from StringIO import StringIO

import tornado.options
import tornado.ioloop
import tornado.web

import tornado.template
import tornado.auth
import tornado.locale

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
import music

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../template/"))


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
            self.redirect("/?status=login")
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


class FileHandler(BaseHandler):
    def get(self):
        self.folder = self.get_argument("folder", "").rstrip("/")
        self.render("../template/file.html")

class Html5UploadFileSliceAPIHandler(BaseHandler):
    def post(self):
        """
        return json
        possible results:
            * success
            * uploading
            * filehash verify failed
        """
        #if not self.current_user:
        #    raise tornado.web.HTTPError(401, "User login required")
        #    return

        self.user_id = "0"#self.current_user.get("user_id", u"").encode("utf8")
        content = base64.b64decode(self.get_argument("content", ""))
        self.filename = self.get_argument("name", "")
        start = long(self.get_argument("start"))
        size = long(self.get_argument("size"))
        #dirname = self.get_argument("dirname")
        tempfile = self.get_argument("tempfile", None)

        if not tempfile:
            tempfile = ".%.7f" % time.time()

        if start + len(content) <= size:
            with open(os.path.join(os.path.dirname(__file__), "../static/temp/%s" % tempfile), "ab") as f:
                f.write(content)

        if size > 0 and start + len(content) == size:
            host = "%s://%s" % (self.request.protocol, self.request.host)
            shutil.move(os.path.join(os.path.dirname(__file__), "../static/temp/%s" % tempfile), "/home/pi/file/%s" % self.filename)
            self.finish({"result": "success"})
            return

        elif os.path.exists(os.path.join(os.path.dirname(__file__), "../static/temp/%s" % tempfile)):
            statinfo = os.stat(os.path.join(os.path.dirname(__file__), "../static/temp/%s" % tempfile))
            self.finish({"result": "uploading", "uploaded_size": statinfo.st_size, "tempfile": tempfile})
            return

        elif start + len(content) > size and os.path.exists(os.path.join(os.path.dirname(__file__), "../static/temp/%s" % tempfile)):
            os.remove(os.path.join(os.path.dirname(__file__), "../static/temp/%s" % tempfile))
            self.finish({"result": "error"})
            return

class FileListAPIHandler(BaseHandler):
    def get(self):
        folder = self.get_argument("folder", "").rstrip("/")
        parent = os.path.dirname(folder)
        for root, folders, files in os.walk('/home/pi/file/%s' % folder):
            break
        self.finish({
            "folder": folder,
            "parent": parent,
            "folders": folders,
            "files": files
        })
