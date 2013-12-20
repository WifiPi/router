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

#import tornado.options
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


UPLOAD_FOLDER = "/home/pi/file"
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/../static/upload"

logger = logging.getLogger(__name__)

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
        logger.info("content_size %i" % len(content))
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
            shutil.move(os.path.join(os.path.dirname(__file__), "../static/temp/%s" % tempfile), "%s/%s" % (UPLOAD_FOLDER, self.filename))
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
        for root, folders, files in os.walk("%s/%s" % (UPLOAD_FOLDER, folder)):
            break
        self.finish({
            "folder": folder,
            "parent": parent,
            "folders": folders,
            "files": files
        })
