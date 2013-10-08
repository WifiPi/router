import os

import json
#import tornado.database


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


#if settings["debug"]:
    #conn = tornado.database.Connection("/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock", "boss", "root", "root")
    #conn = tornado.database.Connection("127.0.0.1", "test", "root", "root")
    #conn1 = tornado.database.Connection("127.0.0.1", "test1", "root", "root")
    #conn2 = tornado.database.Connection("127.0.0.1", "test2", "root", "root")
    #conn3 = tornado.database.Connection("127.0.0.1", "test3", "root", "root")
    #ring = [conn1, conn2] # I love the name Ring
