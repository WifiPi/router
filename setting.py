
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/vendor/')

import json

import tornlite
import torndb


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

conn = tornlite.Connection(os.path.join(os.path.dirname(__file__), "test.db"))

from setting_remote import conn_remote
if conn_remote._db is None:
    conn_remote = conn

ring = [conn]