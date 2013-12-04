
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import socket
import subprocess
import json

#import tornado.template

#loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../template/"))
clients_ip = set()
clients_found = set()
id_file = "/home/pi/.ssh/pi"

def main():
    global clients_ip

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    my_socket.bind(('0.0.0.0',8881))

    #output = subprocess.check_output("ifconfig wlan0", shell=True)
    #ip = output[output.index("inet addr:")+10:].split(" ")[0]

    # config your MySQL server for remote password access
    # change the ip, database, username, password of setting_remote.py

    print 'start service ...'

    while True :
        message_b64 , address = my_socket.recvfrom(8192)
        #print message_b64
        try:
            message = subprocess.check_output("echo '%s'|openssl base64 -d | openssl rsautl -decrypt -inkey %s" % (message_b64, id_file), shell=True)
            print 'from %s message: %s' % (address[0], str(message))

            if message.strip() == "join":
                clients_ip.add(address[0])
                clients_file = json.dumps({"clients": list(clients_ip)})

                with open(os.path.dirname(os.path.abspath(__file__)) + '/../clients.json', 'w+') as f:
                    f.write(clients_file)

                for ip in clients_ip - clients_found:
                    subprocess.check_call("scp -i %s setting_remote.py pi@%s:/var/www/router/" % (id_file, ip), shell=True)
                    subprocess.check_call("ssh -i %s pi@%s 'sudo supervisorctl restart router'" % (id_file, ip), shell=True)
                    clients_found.add(ip)
        except:
            pass

if __name__ == "__main__" :
    main()
