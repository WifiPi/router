import sys
import os
import logging
import cgi

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/vendor')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#import wsgiref.simple_server
#import wsgiref.handlers
#import tornado.wsgi
import tornado.options
import tornado.ioloop
import tornado.web
import tornado.template
import tornado.auth
import tornado.locale

from setting import settings
#from setting import conn

from controller import base
from controller import main
#from controller import api
#from controller import auth
from controller import device
from controller import network
from controller import event
from controller import files

handlers = [
    (r"/", main.MainHandler),
    (r"/event", event.EventHandler),
    (r"/admin/event", event.EventAdminHandler),
    (r"/admin/event/slide/preview", event.EventAdminPreviewHandler),
    (r"/api/event/slide/push", event.EventPushAPIHandler),
    (r"/api/event/slide/list", event.EventListAPIHandler),
    (r"/api/event/slide/load", event.EventLoadAPIHandler),
    (r"/api/event/slide/save", event.EventSaveAPIHandler),
    (r"/api/event/slide/delete", event.EventDeleteAPIHandler),

    (r"/wifi/ping/", device.PingHandler),
    (r"/wifi/login/", device.LoginHandler),
    (r"/wifi/auth/", device.AuthHandler),
    (r"/wifi/portal/", device.PortalHandler),
    (r"/wifi/gw_message.php", device.GWMessageHandler),

    (r"/music", main.MusicHandler),
    (r"/api/play", main.PlayAPIHandler),
    (r"/api/stop", main.StopAPIHandler),
    (r"/api/music/play", main.PlayAPIHandler),
    (r"/api/music/stop", main.StopAPIHandler),
    (r"/api/music/sleep", main.StopAPIHandler),
    (r"/api/music/like", main.StopAPIHandler),
    (r"/api/music/turnoff", main.StopAPIHandler),
    (r"/api/music/shuffle", main.StopAPIHandler),

    (r"/file", files.FileHandler),
    (r"/api/file/upload_html5_slice", files.Html5UploadFileSliceAPIHandler),
    (r"/api/file/list", files.FileListAPIHandler),


    (r"/network", network.NetworkHandler),
    (r"/api/network/change", network.NetworkChangeAPIHandler),
    (r"/api/network/wifi", network.NetworkWifiAPIHandler),
    (r"/api/network/wan", network.NetworkWanAPIHandler),
    (r"/api/network/lan", network.NetworkLanAPIHandler),

    (r"/message", main.MessageHandler),

    (r"/device", device.DeviceHandler),
    (r"/api/device/add", device.DeviceAddAPIHandler),
    (r"/api/device/monitor", device.DeviceMonitorAPIHandler),

    (r"/login", main.LoginHandler),
    (r"/logout", main.LogoutHandler),

    (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'], default_filename='index.html')),

    (r"/library/test/success.html", device.LoginHandler),
]

'''
    (r"/setting", main.SettingHandler),

    (r"/api/profile_img", api.ProfileImgAPIHandler),

    (r"/api/like", api.LikeAPIHandler),
    (r"/api/unlike", api.UnlikeAPIHandler),
    (r"/api/follow", api.FollowAPIHandler),
    (r"/api/unfollow", api.UnfollowAPIHandler),

    (r"/api/post_status", api.PostStatusAPIHandler),
    (r"/api/post_comment", api.PostCommentAPIHandler),

    (r"/auth/google", auth.GoogleHandler),
    (r"/auth/logout", auth.LogoutHandler),
'''

if __name__ == "__main__":
    tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "csv_translations"))
    tornado.locale.set_default_locale("zh_CN")
    tornado.options.define("port", default=8017, help="Run server on a specific port", type=int)
    tornado.options.parse_command_line()
    application = tornado.web.Application(handlers, **settings)
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

