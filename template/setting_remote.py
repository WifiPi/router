
import tornado.database

conn_remote = tornado.database.Connection("{{ ip }}", "{{ database }}", "{{ username }}", "{{ password }}")
