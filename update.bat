rsync -avz . pi@10.0.0.1:/var/www/router/ --delete --exclude=*.log --exclude=*.pyc --exclude=*.mp3 --exclude=.DS_Store --exclude=.git/ --exclude=.gitignore --exclude=static/temp/ --exclude=static/cache/
#ssh pi@10.0.0.1 "cd /var/www/router/; python compile.py; find /var/www/router/|grep '.py$'|xargs rm"
ssh pi@10.0.0.1 "cd /var/www/router/; python compile.py"
