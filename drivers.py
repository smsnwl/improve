import math
import RPi.GPIO as GPIO
import threading
import time
import csv

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class Double_stepper:
    def __init__(self, pen0, pdr0, pul0, pen1, pdr1, pul1):
        GPIO.setup([pen0, pdr0, pul0, pen1, pdr1, pul1], GPIO.OUT, initial = 0)
        self.pen0 = pen0
        self.pdr0 = pdr0
        self.pul0 = pul0
        self.pen1 = pen1
        self.pdr1 = pdr1
        self.pul1 = pul1

    def Step_a(self, nsa,t):
        GPIO.setmode(GPIO.BCM)
        count0=0
        if nsa == 0:
            dia = 0
        elif nsa < 0:
            dia = 0
        else:
            dia = 1
        for v in range(0,round(abs(nsa))):
            GPIO.output(self.pul0,1)
            time.sleep(abs(t/nsa))
            GPIO.output(self.pul0,0)
            count0 += 1
        # with open("data.csv", "a") as datafile:
        #     datafile.write("  %d"%count0)

    def Step_b(self,nsb,t):
        GPIO.setmode(GPIO.BCM)
        count1=0
        if nsb == 0:
            dib = 0
        elif nsb < 0:
            dib = 0
        else :
            dib = 1
        for i in range(0,round(abs(nsb))):
            GPIO.output(self.pul1,1)
            time.sleep(abs(t/nsb))
            GPIO.output(self.pul1,0)
            count1+=1
        # with open("data.csv", "a") as datafile:
        #     datafile.write(",  %d"%count1)

    def double_step(self, nsa, nsb, t):
        self.nsa = round(nsa)
        self.nsb = round(nsb)
        self.t = t
        nsk = max(round(abs(self.nsa)),round(abs(self.nsb)))
        tx = 1 + nsk /200 * 0.2            
        t = tx
        threads=[]
        threads.append(threading.Thread(target=self.Step_a(nsa,t)))
        threads.append(threading.Thread(target=self.Step_b(nsb,t)))
        for t in threads:
            t.start()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)

    # ds = Double_stepper(26,19,13,6,5,0)
    # bd_xz = Double_stepper(22,27,17,18,15,14)
    bd_sj = Double_stepper(22,27,17,11,9,10)

    nsa=50
    nsb=170
    t=5

    # ds.double_step(nsa,nsb,t)
    # bd_xz.double_step(-nsa,nsb,t)
    bd_sj.double_step(nsa,-nsb,t)


