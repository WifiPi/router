import os

import json
import tornado.database


settings = {
    #"xsrf_cookies": True,
    "static_path": os.path.join(os.path.dirname(__file__), "static/"),
    "AmazonAccessKeyID": "AKIAJC6EF76YUIBCYWRQ",
    "AmazonSecretAccessKey": "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",
    "email_sender": "kernel1983@gmail.com",
    "cookie_secret": "Ozb11oomjAGckaoL5OSXGe34pyCz7EQxnjo67p1ocad=",
    "login_url": "/login",
    "debug": True,
}

conn = tornado.database.Connection("127.0.0.1", "test", "root", "root")

ring = [conn]