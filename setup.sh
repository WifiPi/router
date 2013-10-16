#!/bin/bash
# run as root

cp testing/etc/ppp/peers/dsl-provider /etc/ppp/peers/
cp testing/etc/ppp/pap-secrets /etc/ppp/
pon dsl-provider


## apt remove all the GUI of debian

##sudo apt-get remove task-desktop

##sudo apt-get purge xorg
##sudo apt-get autoremove

#apt-get remove -y --purge x11-common
#apt-get autoremove

#apt-get update

## install packages

apt-get install -y wireless-tools
apt-get install -y hostapd
apt-get install -y dnsmasq
apt-get install -y pppoe
apt-get install -y mpg123
apt-get install -y supervisor

#host=192.168.1.100
#wget --recursive http://$host/
#mv $host testing

cp testing/etc/default/hostapd /etc/default/
cp testing/etc/hostapd/hostapd.conf /etc/hostapd/

cp testing/etc/dnsmasq.conf /etc/
cp testing/etc/dhcp/dhclient.conf /etc/dhcp/

cp testing/etc/network/interfaces /etc/network/
cp testing/etc/network/if-pre-up.d/iptables /etc/network/if-pre-up.d/
cp testing/etc/iptables.up.rules /etc/
chmod +x /etc/network/if-pre-up.d/iptables

cp testing/etc/supervisor/conf.d/router.conf /etc/supervisor/conf.d/
supervisorctl reload

cp testing/etc/sysctl.conf /etc/
echo "1" > /proc/sys/net/ipv4/ip_forward

cp testing/etc/init.d/watch-wlan0 /etc/init.d/
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

