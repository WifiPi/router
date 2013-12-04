
import sys
import os

import socket
import subprocess
import json

clients_ip = set()

def main():
    global clients_ip

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    my_socket.bind(('0.0.0.0',8881))

    print 'start service ...'

    while True :
        message_b64 , address = my_socket.recvfrom(8192)
        #print message_b64
        try:
            message = subprocess.check_output("echo '%s'|openssl base64 -d | openssl rsautl -decrypt -inkey ~/.ssh/id_rsa" % message_b64, shell=True)
            print 'from %s message: %s' % (address[0], str(message))

            if message.strip() == "join":
                clients_ip.add(address[0])
                clients_file = json.dumps({"clients": list(clients_ip)})

                with open(os.path.dirname(os.path.abspath(__file__)) + '/clients.json', 'w+') as f:
                    f.write(clients_file)

                for ip in clients_ip:
                    subprocess.check_call("ssh pi@%s 'ls'" % ip, shell=True)
        except:
            pass

if __name__ == "__main__" :
    main()
