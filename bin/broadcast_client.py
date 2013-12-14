
import sys
import socket
import subprocess
import time

def main(message):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        my_socket.sendto(message, ('<broadcast>', 8881))
    except:
        pass
    my_socket.close()

if len(sys.argv) < 2:
    print 'use: python broadcast_client.py "message"'
else:
    message = sys.argv[1]
    message_b64 = subprocess.check_output("echo '%s' | openssl rsautl -encrypt -inkey /home/pi/.ssh/pi.pub.pem -pubin|openssl base64" % message, shell=True)
    while True:
        main(message_b64)
        print message
        time.sleep(30)
