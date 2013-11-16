
cd /root/
rm -r .ssh/
rm .bash_history

cd /home/pi/
#rm -r .ssh/
rm -r .aptitude/
rm .bash_history
rm .viminfo
rm -r .vim

cd /home/pi/testing/

echo "" > wifi_ping.log
echo "" > dhcp_hook.log

find . |grep ".pyc$"|xargs rm
python -c "import compileall; compileall.compile_dir(r'.')"
find . |grep ".py$"|xargs rm
rm update.bat
rm clear.bat

cd /home/pi/testing/static/temp/
rm *
cd /home/pi/testing/static/cache/
rm *

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