import subprocess
import time

p = None

def play(filename):
    global p
    stop()
    p = subprocess.Popen(["mpg123", filename]) #mpg123

def stop():
    global p
    if p:
        p.terminate()
        p = None

if __name__ == '__main__':
    play("15bce0a605beaa38e669f026d5697a5e.mp3")
    time.sleep(10)
    stop()
