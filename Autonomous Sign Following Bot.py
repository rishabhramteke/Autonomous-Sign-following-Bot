import picamera.array
import picamera
import cv2
import numpy as np
import time 
import RPi.GPIO as gpio

gpio.cleanup()
gpio.setmode(gpio.BCM)
gpio.setup(17,gpio.OUT)
gpio.setup(18,gpio.OUT)
gpio.setup(22,gpio.OUT)
gpio.setup(23,gpio.OUT)
gpio.setup(5,gpio.OUT)
gpio.setup(6,gpio.IN)
l_m = gpio.PWM(23,1000)    #l_m - left side speed control
r_m = gpio.PWM(17,1000)    #r_m - right side speed control
gpio.output(17,False)
gpio.output(18,False)
gpio.output(22,False)
gpio.output(23,False)

def reverse(tf):
    #init()
    gpio.output(17,False)  #17(+),18(-) - left side motors
    gpio.output(18,True)   #22(-),23(+) - right side motors
    gpio.output(22,True)
    gpio.output(23,False)
    time.sleep(tf)
    #gpio.cleanup()

def forward(x):
    if(x==100):
        l_m.ChangeDutyCycle(x)
        r_m.ChangeDutyCycle(x-3)
    else:
        l_m.ChangeDutyCycle(x+5)
        r_m.ChangeDutyCycle(x-3)

def stop(tf):
    
    l_m.ChangeDutyCycle(0)
    r_m.ChangeDutyCycle(0)
    gpio.output(18,False)
    gpio.output(22,False)
    
    time.sleep(tf)
    #gpio.cleanup()

def left(tf):
    l_m.ChangeDutyCycle(100-x)
    r_m.ChangeDutyCycle(x)
    gpio.output(18,False)
    gpio.output(22,True)
    time.sleep(tf)
    gpio.output(22,False)

def right(tf):
    r_m.ChangeDutyCycle(100-x)
    l_m.ChangeDutyCycle(x)
    gpio.output(18,True)
    gpio.output(22,False)
    time.sleep(tf)
    gpio.output(18,False)

def U_turn(tf):
    left(tf)
    
TRIG= 5
ECHO= 6 
    


def distance():
    gpio.output(TRIG,False)
    gpio.output(TRIG,True)
    time.sleep(0.00001)
    gpio.output(TRIG,False)
    ct=time.time()
    pulse_start=0
    pulse_end=0
    while gpio.input(ECHO)==0:
        pulse_start = time.time()
        if((pulse_start-ct) > 1):
            pulse_end=pulse_start
            break
    while gpio.input(ECHO)==1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    
    Distance= pulse_duration * 17150

    Distance= round(Distance, 2)
    print("Distance:", Distance, "cm")
    
		
    #gpio.cleanup()
    return Distance



imgleft= cv2.imread('/home/pi/Downloads/left.jpeg',0)
imgright= cv2.imread('/home/pi/Downloads/right.jpeg',0)
imgu = cv2.imread('/home/pi/Downloads/uturn.jpeg',0)
imgstop = cv2.imread('/home/pi/Downloads/stop.jpeg',0)
imgspeed10 = cv2.imread('/home/pi/Downloads/speed10.jpeg',0)
imgspeed5 = cv2.imread('/home/pi/Downloads/speed5.jpeg',0)
imgfinish= cv2.imread('/home/pi/Downloads/finish.jpeg',0)
imgspeed15 = cv2.imread('/home/pi/Downloads/speed15.jpeg',0)

surf = cv2.xfeatures2d.SURF_create(200,4,2,False,True)

kpleft, desleft = surf.detectAndCompute(imgleft,None)
kpright, desright = surf.detectAndCompute(imgright,None)
kpu, desu = surf.detectAndCompute(imgu,None)
kpstop, desstop = surf.detectAndCompute(imgstop,None)
kpspeed10, desspeed10 = surf.detectAndCompute(imgspeed10,None)
kpspeed5, desspeed5 = surf.detectAndCompute(imgspeed5,None)
kpfinish, desfinish = surf.detectAndCompute(imgfinish,None)
kpspeed15,desspeed15 = surf.detectAndCompute(imgspeed15,None)

flag=0
camera = picamera.PiCamera()
camera.resolution = (640,480)
raw = picamera.array.PiRGBArray(camera,size=(640,480))

l_m.start(100)
r_m.start(100)

forward(100)

x=100

d1=distance()
d2=d1
for frame in camera.capture_continuous(raw,format='bgr',use_video_port=True):
    raw.truncate(0)
    image=frame.array
    roi = image[60:320, 0:320]
    img2 = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    cv2.imshow('crop', roi)
    if(x==100):
        y=36
    else:
        y=30
    dist=distance()
    d1=d2
    d2=dist
    if(dist>y):
        forward(x)
    if((d2-d1)>20 or (d1-d2)>20):
        continue
    if(dist<=0):
        continue
    if(dist<y):
        stop(0.5)
        print("stop")
    
    # find the keypoints and descriptors with surf
        kp2, des2 = surf.detectAndCompute(img2,None)
        if (len(kp2)<10):
            continue
        # BFMatcher
        bf = cv2.BFMatcher()
        matchesleft = bf.knnMatch(desleft,des2, k=2)
        matchesright = bf.knnMatch(desright,des2, k=2)
        matchesu = bf.knnMatch(desu,des2, k=2)
        matchesstop = bf.knnMatch(desstop,des2, k=2)
        matchesspeed10 = bf.knnMatch(desspeed10,des2, k=2)
        matchesspeed5 = bf.knnMatch(desspeed5,des2, k=2)
        matchesfinish = bf.knnMatch(desfinish,des2, k=2)
        matchesspeed15 = bf.knnMatch(desspeed15,des2, k=2)
    
        # Apply ratio test
        goodleft = []
        goodright = []
        goodu = []
        goodstop = []
        goodspeed5 = []
        goodspeed10 = []
        goodfinish = []
        goodspeed15 = []
    
        for m,n in matchesleft:
            if m.distance < 0.75*n.distance:
                goodleft.append([m])
        ratleft = len(goodleft)/len(kpleft)
        if(ratleft>0.6):
            print('left')
            if(x==100): 
                left(0.73)
            else:
                left(160)
            forward(x)
            continue
            
        for m,n in matchesright:
            if m.distance < 0.75*n.distance:
                goodright.append([m])
        ratright = len(goodright)/len(kpright)
        if(ratright>0.6):
            print('right')
            if(x==100):
                right(1.1)
            else:
                right(130/x)
            forward(x)
            continue
            
        for m,n in matchesu:
            if m.distance < 0.75*n.distance:
                goodu.append([m])
        ratu = len(goodu)/len(kpu)
        if(ratu>0.6):
            print('uturn')
            U_turn(175/x)
            forward(x)
            continue
            
        for m,n in matchesspeed10:
            if m.distance < 0.75*n.distance:
                goodspeed10.append([m])
        ratspeed10 = len(goodspeed10)/len(kpspeed10)
        if(ratspeed10>0.6):
            print('speed change to 10')
            x=67
            right(8/x)
            forward(x)
            time.sleep(1)
            continue
        
        for m,n in matchesspeed15:
            if m.distance < 0.75*n.distance:
                goodspeed15.append([m])
        ratspeed15 = len(goodspeed15)/len(kpspeed15)
        if(ratspeed15>0.6):
            print('speed change to 15')
            x=100
            right(9/x)
            forward(x)
            time.sleep(1)
            continue
            
        for m,n in matchesspeed5:
            if m.distance < 0.75*n.distance:
                goodspeed5.append([m])
        ratspeed5 = len(goodspeed5)/len(kpspeed5)
        if(ratspeed5>0.6):
            print('speed change to 5')
            x=33
            forward(x)
            time.sleep(1)
            continue
            
        for m,n in matchesstop:
            if m.distance < 0.75*n.distance:
                goodstop.append([m])
        ratstop = len(goodstop)/len(kpstop)
        if(ratstop>0.6):
            print('stop')
            stop(3)
            forward(x)
            time.sleep(2)
            continue
        
        for m,n in matchesfinish:
            if m.distance < 0.75*n.distance:
                goodfinish.append([m])
        ratfinish = len(goodfinish)/len(kpfinish)
        if(ratfinish>0.5):
            print('finish')
            gpio.cleanup()
            break
    
                        
        
            
    if cv2.waitKey(1) &0xFF == ord('q'):
        break

gpio.cleanup()
#camera.release()
cv2.destroyAllWindows()


