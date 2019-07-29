from drivers import Stepper
from drivers import Stepper_slow
from drivers import Double_stepper
from drivers import a1
from drivers import a4
from drivers import Button
from drivers import Relay
import threading
import csv
import drivers
import math
import time
import sys
import RPi.GPIO as GPIO

global l0,l1,l2,l3,l4,p0,B0,p1,B1,b0,b1,ms
# dir_steper:0or1:  0:down/1:up
#t0 预热时间120秒
# t1 加油时间
# t2 加面糊时间
# t3 第一面加热时间（加蛋前）
# t4 加蛋后加热时间 
# t5 烙饼的第二面
# tw 五边运动时间
# tb 摆动旋转时间
# tj 卷饼展饼时间
# tz 升降展饼时间
t0 = 120; t1 = 2; t2 = 5; t3 = 40; t4 = 25; t5 =35
t0=t2=t3=t4=t5=1
tw = 3; tb = 3; tj = 3; tz = 3
ns = 1110  #下降到可摊饼高度
nsc = 1090  # 铲饼所需步数
        
def wubi(p0,b0,p1,b1,t1=4):    
    p0 = p0
    B0 = math.atan(b0)
    a10 = a1(p0,B0,)
    a40 = a4(p0,B0)
    p0 = p1
    B0 = math.atan(b1)
    a11 = a1(p0,B0)
    a41 = a4(p0,B0)
    da1 = (a11 -a10)*180/math.pi
    da4 = (a41- a40)*180/math.pi
    step_da1 = round(4*200*da1/360)
    step_da4 = round(4*200*da4/360)

    ds.double_step(step_da1, step_da4,t1)
    time.sleep(1)
    return
def SJ(dir,ns,cond=lambda:True):
    ks_sj = sj.rotate(dir,ns,btnZ.getinput)
    print("ks_sj",ks_sj)
    return
def BD(dir,bns,cond=lambda:True):
    ks_bd = bd.rotate(dir,bns,btnbd.getinput)
    print("ks_bd",ks_bd)
    return
def XZ(dir,ns,cond=lambda:True):
    ks_xz = xz.rotate(dir,ns,btnxz.getinput)
    print("ks_xz",ks_xz)
    return
    
def BDXZ(ms, msx,t2, cond=lambda:True):
    bd_xz.double_step(ms, msx,t2)
    return

def BDSJ(ms, msx,t2, cond=lambda:True):
    bd_sj.double_step(ms, msx,t2)
    return

def resetZ():
    sj.rotate(1, ns, btnZ.getinput)    #升起到传感器0位

def resetbd():
    bd.rotate(0,120)
    time.sleep(1)
    bd.rotate(1,300,btnbd.getinput)  #摆动到鏊子边缘

def resetxz():
    xz.rotate(0,420,btnxz.getinput)   #旋转到可铲饼0位
        
    # work
def Work_prepare():
    ST = time.time()
    print("step0:prepare")
    print("reset....")
    resetZ()
    resetbd()
    resetxz()

    print("reset-end")
    print("helt-start:Heltting....")
    print("aozi-rotateing....")
    #鏊子旋转启动
    Re.trigger(0)
    #鏊子加热启动
    t0 = 3    # 实际约120秒
    time.sleep(t0)   # t0 鏊子预热时间
    T0 = time.time()-ST
    print("Ready  Time0:", round(T0))

def Step1():
    print("step1:add & coating oil")
    TS =time.time()
    #加油（泵启动）
    time.sleep(t1)   # t1 加油时间
    #电磁铁吸起毛刷
    wubi(300,1,300,0,tw)      #刷匀油
    wubi(300,0,300,1,tw)      #五边复位
    # 电磁铁放下毛刷
    wubi(300,1,280,1.3,tw-1)   # 五边移动到鸡蛋容器处    
    T1 = time.time()-TS
    print("T1:", round(T1),"s")
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T1)

def Step2():
    # 加面糊（泵启动）
    print("step2:Add & coating batter")
    TS =time.time()
    bd.rotate(1,100)   #ns: 竹蜻蜓摆动到摊饼位置（鏊子中间）
    ks0 =  sj.rotate(0, ns)    #:下降到可摊饼高度
    time.sleep(t2)   # t2 加面糊时间
    for j in range(4):
        sj.rotate(1, 10)    #提升（防止带饼）
        time.sleep(2)
        j = j +1
    time.sleep(3)
    resetZ()
    # ks3 =  sj.rotate(1, ns,btnZ.getinput)    #高度复位
    time.sleep(t3)   # t3 第一面加热时间（加蛋前）
    T2 = time.time()-TS
    print("T2:", round(T2),"s")
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T2)

def Step3():
    #加蛋
    print("step3: add & coating eggs")
    TS =time.time()
    ks1 =  sj.rotate(0, ns-50)    #加蛋高度
    wubi(280,1.3,300,0,tw)   # 五边加鸡蛋    
    wubi(300,0,280,1.3,tw)   # 五边复位
    wubi(280,1.3,240,1.5,tw-1)   # 五边移动到调料处
    time.sleep(5)
    resetZ()
    time.sleep(t4)   # t4 加蛋后加热时间 
    bd.rotate(0,120)   #摆臂复位
    time.sleep(1)
    bd.rotate(1,50,btnbd.getinput)   #摆臂复位
    T3 = time.time()-TS
    print("T3:", round(T3),"s")
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T3)

def Step4():
    #铲饼
    print("step4: Shovel cake....")
    TS =time.time()
    ks2 =  sj.rotate(0, nsc)    #降到铲饼高度
    bd.rotate(0,80)   #铲饼
    time.sleep(2)
    bd.rotate(1,120,btnbd.getinput)   #后撤到卷饼起始位置
    time.sleep(0.5)
    T4 = time.time()-TS
    print("T4:", round(T4),"s")
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T4)

def Step5():
    #提饼展饼
    print("step5: putup & spread cake  ")
    TS =time.time()
    if True:  # ResetButton == on:
        resetZ()
        resetbd()
        resetxz()
        ks2 =  sj.rotate(0, nsc)    #降到铲饼高度
    bd.rotate(0,40)   #到卷饼起始位置
    Re.trigger(1)   #鏊子停
    time.sleep(4)

########
    sj.rotate(1,3*ns)   ####升到翻饼足够高度
    bd.rotate(1,200,btnbd.getinput)   #后撤至鏊子边缘，待展饼位置
    BDSJ(-120,-2.5*ns,3)    #摆动，降高度——展饼
    BDXZ(-60,-350,t2)   #展饼
    Re.trigger(0)
########

    resetZ()   #复位
    bd.rotate(1,200,btnbd.getinput)   #旋转复位
    resetxz()
    Re.trigger(0)   #鏊子旋转
    time.sleep(t5)    #烙饼的第二面
    T5 = time.time()-TS
    print("T5:", round(T5),"s")
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T5)

def Step7():
    # 涂酱
    print("step7: Spread sauce")
    TS =time.time()
    wubi(230,1.3,300,0,tw)
    wubi(300,0,230,1.3,tw)
    wubi(230,1.3,200,1.6,tw-1)
    T7 = time.time() - TS
    print("T7:", round(T7),"s")
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T7)

def Step8():
    # 加薄脆
    print("step8: add Bocui")
    TS =time.time()
    Re.trigger(1)
    wubi(200,1.6,300,0,tw)
    wubi(300,0,200,1.6,tw)
    wubi(200,1.6,300,1,tw-1)
    T8 = time.time() - TS
    print("T8:", round(T8),"s")
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T8)

def Step9():
    # 折叠
    print("Step9:folding....")
    TS =time.time()
    for i in range(2):
        Re.trigger(1)
        resetZ()
        resetbd()
        resetxz()
        ks = sj.rotate(0, nsc)    #降到铲饼高度
        bd.rotate(0,45)   #铲饼
        sj.rotate(1,0.5*ns)
        BDXZ(-50,50,3)
        Re.trigger(0)
        # if btnaz.getinput == 1:
        #     Re.trigger(1)
        time.sleep(1)
    T9 = time.time()-TS
    print("T9", round(T9))
    with open("data.csv", "a") as logfile:
        logfile.write(", %d"%T9)

          
    # time.sleep(1)  #等待折叠后移动
    # # time.sleep(30)  #等待折叠后移动
    # t = time.time()-ts
    # print("t",t)

    
def Work_cycle():
    TS = time.time()
    Work_prepare()
    for i in range(2):
        with open("data.csv", "a") as logfile:
            logfile.write(time.strftime("%Y-%m-%d-%H-%M-%S"))
            logfile.write(", %d"%i) 
        print("No.",i,)
        ts = time.time()
        Step1()
        Step2()
        Step3()
        Step4()
        Step5()
#        Step6()
        Step7()
        Step8()
        Step9()
        
        t_onetime = time.time()-TS
        print("t_onetime",t_onetime)
        with open("data.csv", "a") as logfile:
            logfile.write(", %d\n"%t_onetime)
    t_all = time.time()-TS
    print("t_all_time:", t_all)
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)

    global tw,tb
    tw = 3; tb = 3;
    ds = Double_stepper(26,19,13,6,5,0)
    bd_xz = Double_stepper(22,27,17,18,15,14)
    bd_sj = Double_stepper(22,27,17,11,9,10)
    sj = Stepper(11,9,10)
    bd = Stepper_slow(22,27,17)
    xz = Stepper_slow(18,15,14)
    Re = Relay(2)
    
    # Buttons
    btnZ = Button(21)
    btnbd = Button(20)
    btnxz = Button(16)
    btnaz = Button(12)

    Work_cycle()
    
    GPIO.cleanup()
