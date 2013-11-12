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

import nomagic
#import nomagic.auth
import nomagic.feeds

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



class UploadMp3Html5SliceAPIHandler(BaseHandler):
    def get(self):
        #if not self.current_user:
        #    raise tornado.web.HTTPError(401, "User login required")
        #    return

        filehash = self.get_argument("filehash")
        fileinfo = nomagic._get_entity_by_id(filehash)
        if fileinfo and os.path.exists(os.path.join(os.path.dirname(__file__), "../static/cache/"+filehash+".mp3")):
            self.finish({"result":"exists"})
        elif os.path.exists(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash)):
            statinfo = os.stat(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash))
            self.finish({"result":"uploading", "uploaded_size": statinfo.st_size})
        else:
            self.finish({"result":"not found"})

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

        #self.user_id = self.current_user.get("user_id", u"").encode("utf8")
        self.user_id = "0"
        content = base64.b64decode(self.get_argument("content", ""))
        self.filename = self.get_argument("name", "")
        start = long(self.get_argument("start"))
        #end = long(self.get_argument("end"))
        size = long(self.get_argument("size"))
        filehash = self.get_argument("filehash")

        #print start, len(content)
        if start + len(content) <= size:
            with open(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash), "ab") as f:
                f.write(content)

        if size > 0 and start + len(content) == size:
            with open(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash), "rb") as f:
                content = f.read()
            print filehash, hashlib.md5(content).hexdigest()
            if filehash != hashlib.md5(content).hexdigest():
                os.remove(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash))
                self.finish({"result":"filehash verify failed"})
                return
        elif start + len(content) > size and os.path.exists(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash)):
            os.remove(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash))
            self.finish({"result":"error"})
            return
        elif os.path.exists(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash)):
            statinfo = os.stat(os.path.join(os.path.dirname(__file__), "../static/temp/"+filehash))
            self.finish({"result":"uploading", "uploaded_size": statinfo.st_size})
            return

        """
        mem = StringIO(content)
        id3 = ID3(mem)
        id3info = {}
        if id3.has_tag:
            if id3.genre != None and id3.genre >= 0 and \
                   id3.genre < len(id3.genres):
                genre = id3.genres[id3.genre]
            else:
                genre = 'Unknown'

            if id3.track != None:
                track = str(id3.track)
            else:
                track = 'Unknown'

            id3info["Title"] = detect_encoding(id3.title)
            id3info["Artist"] = detect_encoding(id3.artist)
            id3info["Album"] = detect_encoding(id3.album)
            id3info["Track"] = detect_encoding(track)
            id3info["Year"] = detect_encoding(id3.year)
            id3info["Comment"] = detect_encoding(id3.comment)
            id3info["Genre"] = detect_encoding(genre)

            id3.write()

        title = self.filename[:-4] if self.filename.endswith(".mp3") else self.filename
        title = id3info["Title"] if id3info.get("Title") else title
        artist = id3info["Artist"] if id3info.get("Artist") else ""
        album = id3info["Album"] if id3info.get("Album") else ""

        #content = mem.getvalue()
        """
        filehash = hashlib.md5(content).hexdigest()
        with open(os.path.join(os.path.dirname(__file__), "../static/cache/"+filehash+".mp3"), "wb") as f:
            f.write(content)
        fileinfo, user = nomagic.feeds.update_fileinfo(filehash, self.user_id)

        host = self.request.protocol + "://" + self.request.host
        self.finish({#"host": host,
            #"music_file": "/static/cache/%s.mp3" % filehash,
            #"files_count": len(user.get("files", [])),
            #"id3info": id3info,
            #"artist": artist,
            #"album": album,
            #"title": title,
            "result": "success"})


class AddMp3ByFilehashAPIHandler(BaseHandler):
    def post(self):
        #if not self.current_user:
        #    raise tornado.web.HTTPError(401, "User login required")
        #    return

        filehash = self.get_argument("filehash")
        #self.user_id = self.current_user.get("user_id", u"").encode("utf8")
        self.user_id = "0"
        #user = nomagic._get_entity_by_id(self.user_id)
        fileinfo, user = nomagic.feeds.update_fileinfo(filehash, self.user_id)
        self.finish()


