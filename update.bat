rsync -avz . pi@192.168.10.1:~/testing/ --delete --exclude=*.log --exclude=*.pyc --exclude=*.mp3 --exclude=.DS_Store --exclude=.git/ --exclude=.gitignore --exclude=static/temp/ --exclude=static/cache/
#ssh pi@192.168.10.1 "python ~/testing/compile.py; find ~/testing/|grep '.py$'|xargs rm"
