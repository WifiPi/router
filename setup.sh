#!/bin/bash
# run as root

cp static/8188eu.ko /lib/modules/3.6.11+/kernel/drivers/net/wireless/
depmod -a
modprobe 8188eu

dpkg -i static/libpcap0.8_1.3.0-1_armhf.deb
dpkg -i static/ppp_2.4.5-5.1_armhf.deb
dpkg -i static/pppoe_3.8-3_armhf.deb

cp /var/www/router/etc/ppp/peers/dsl-provider /etc/ppp/peers/
cp /var/www/router/etc/ppp/pap-secrets /etc/ppp/
pon dsl-provider


## apt remove all the GUI of debian

##sudo apt-get remove task-desktop

##sudo apt-get purge xorg
##sudo apt-get autoremove

#apt-get remove -y --purge x11-common
#apt-get autoremove

apt-get update

## install packages

apt-get install -y wireless-tools
apt-get install -y hostapd
apt-get install -y dnsmasq
apt-get install -y pppoe
apt-get install -y mpg123
apt-get install -y supervisor

apt-get install -y nginx
apt-get install -y mysql-server
apt-get install -y python-mysqldb

apt-get install -y mtools
apt-get install -y ntfsprogs
apt-get install -y e2fsprogs

#host=192.168.1.100
#wget --recursive http://$host/
#mv $host testing

cp /var/www/router/etc/default/hostapd /etc/default/
cp /var/www/router/etc/hostapd/hostapd.conf /etc/hostapd/

cp /var/www/router/etc/dnsmasq.conf /etc/
cp /var/www/router/etc/dhcp/dhclient.conf /etc/dhcp/

cp /var/www/router/etc/network/interfaces /etc/network/
cp /var/www/router/etc/network/if-pre-up.d/iptables /etc/network/if-pre-up.d/
cp /var/www/router/etc/iptables.up.rules /etc/
chmod +x /etc/network/if-pre-up.d/iptables

cp /var/www/router/etc/supervisor/conf.d/router.conf /etc/supervisor/conf.d/
supervisorctl reload

cp /var/www/router/etc/nginx/sites-enabled/router /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
/etc/init.d/nginx reload

cp /var/www/router/etc/sysctl.conf /etc/
echo "1" > /proc/sys/net/ipv4/ip_forward

cp /var/www/router/etc/init.d/watch-wlan0 /etc/init.d/
chmod +x /etc/init.d/watch-wlan0
update-rc.d watch-wlan0 defaults

# TODO
# 1. see if we need to change something in eth0 dhcp to shorten the booting time
# 2. disable hostapd and dnsmasq's init.d script, both invoked by watch-wlan0 script
#update-rc.d hostapd disable 2
#update-rc.d dnsmasq disable 2
# 3. remove sshd


/etc/init.d/networking restart
/etc/init.d/watch-wlan0 restart
#/etc/init.d/hostapd restart
#/etc/init.d/dnsmasq restart
## or
#reboot

