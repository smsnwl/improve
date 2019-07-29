import RPi.GPIO as GPIO
import threading
import time
import csv

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pin_en0=22
pin_dir0=27
pin_pul0=17
pin_en1=11
pin_dir1=9
pin_pul1=10
GPIO.setup([pin_en0,pin_dir0,pin_pul0,pin_en1,pin_dir1,pin_pul1],GPIO.OUT,initial=0)


def Step_a():
    GPIO.output([pin_en0],GPIO.LOW)
    if dia==0:
        GPIO.output(pin_dir0,GPIO.LOW)
    if dia==1:
        GPIO.output(pin_dir0,GPIO.HIGH)
    count0=0
    if nsa==0:
       count0+=0
    else:
        for v in range(0,nsa):
            GPIO.output(pin_pul0,GPIO.HIGH)
            time.sleep(t/nsa)
            GPIO.output(pin_pul0,GPIO.LOW)
            count0+=1
    with open("data1.csv", "a") as datafile:
        datafile.write("  %d"%count0)
def Step_b():
    GPIO.output([pin_en1],GPIO.LOW)
    if dib==0:
        GPIO.output(pin_dir1,GPIO.LOW)
    if dib==1:
        GPIO.output(pin_dir1,GPIO.HIGH)
    count1=0
    if nsb==0:
        count1+=0
    else:
        for i in range(0,nsb):
            GPIO.output(pin_pul1,GPIO.HIGH)
            time.sleep(t/nsb)
            GPIO.output(pin_pul1,GPIO.LOW)
            count1+=1
    with open("data1.csv", "a") as datafile:
                datafile.write(",  %d\n"%count1)
def double_step(nsa,dia,nsb,dib,t):
    threads=[]
    threads.append(threading.Thread(target=Step_a))
    threads.append(threading.Thread(target=Step_b))
    for t in threads:
        t.start()
if __name__ == '__main__':
    nsa=50
    dia=0
    nsb=170
    dib=1
    t=5

    double_step(nsa,dia,nsb,dib,t)


