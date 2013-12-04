
cd /root/
rm -r .ssh/
rm .bash_history

cd /home/pi/
#rm -r .ssh/
rm -r .aptitude/
rm -r .vim
rm .viminfo
rm .bash_history

cd /var/www/router/

echo "" > wifi_ping.log
echo "" > dhcp_hook.log

find . |grep ".pyc$"|xargs rm
python -c "import compileall; compileall.compile_dir(r'.')"
find . |grep ".py$"|xargs rm
rm thirdpart/ -r
rm clients.json

rm update.bat
rm setup.sh
rm clear.bat
chown -R pi:pi *

#cd /var/www/router/static/temp/
#rm *
#cd /var/www/router/static/cache/
#rm *

cd /var/log/
rm *.0
rm *.1
rm *.gz
echo "" > dpkg.log
echo "" > daemon.log
echo "" > auth.log
echo "" > bootstrap.log
echo "" > messages
echo "" > debug
echo "" > syslog
echo "" > aptitude
echo "" > webiopi

cd /var/log/supervisor/
echo "" > supervisord.log
rm router*

#deb
cd /var/cache/apt/archives/
rm *.deb

cd /var/backups/
rm *.gz