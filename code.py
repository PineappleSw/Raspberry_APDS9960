from apds9960.const import *
from apds9960 import APDS9960
import RPi.GPIO as GPIO
import smbus
from time import sleep
import sys
import Adafruit_ADS1x15 
import os
import time

M_RIGHT = 20
M_LEFT = 21

adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
GAIN = 1
port = 1
bus = smbus.SMBus(port)

k = 0
s = 20
h = 100
l = 21
t = 1

apds = APDS9960(bus)
def intH(channel):
    print("INTERRUPT")

GPIO.setmode(GPIO.BCM)
GPIO.setup(7, GPIO.IN)

GPIO.add_event_detect(7, GPIO.FALLING, callback = intH)

dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
}

def setup(*ports):
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	for port in ports:
		GPIO.setup(port, GPIO.OUT)
		GPIO.output(port, GPIO.LOW)
		
def stop_all():
	GPIO.output(M_LEFT, GPIO.LOW)
	GPIO.output(M_RIGHT, GPIO.LOW)
		
setup(M_RIGHT, M_LEFT)

try:
    # Interrupt-Event hinzufuegen, steigende Flanke

    apds.setProximityIntLowThreshold(50)
    pinPWM = 13
    GPIO.setup(pinPWM, GPIO.OUT)
    pwm = GPIO.PWM(pinPWM, 1000)
    pwm.start(100)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(l)
    pwm.ChangeFrequency(1000)
    print("speed = 30%")
    print("Gesture Test")
    print("============")
    apds.enableGestureSensor()
    while True:
        values = [0]*4
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN)
        sleep(0.5)
        if apds.isGestureAvailable():
            motion = apds.readGesture()
            print("Gesture={}".format(dirs.get(motion, "unknown")))
            
            if motion == APDS9960_DIR_UP:
                if k * s < h:
                    k = k + 1
                
                pwm.ChangeDutyCycle(k * s)
                print(k * s)
                
            if motion == APDS9960_DIR_DOWN:
                if k * s >= l:
                    k = k - 1
                pwm.ChangeDutyCycle(k * s)
                print(k* s)
                
            if motion == APDS9960_DIR_RIGHT: 
                GPIO.output(M_RIGHT, GPIO.LOW)
                GPIO.output(M_LEFT, GPIO.HIGH)
                time.sleep(t)
                GPIO.output(M_RIGHT, GPIO.LOW)
                GPIO.output(M_LEFT, GPIO.LOW)
                print('dc = right')
           
            if motion == APDS9960_DIR_LEFT: 
                GPIO.output(M_LEFT, GPIO.LOW)
                GPIO.output(M_RIGHT, GPIO.HIGH)
                time.sleep(t)
                GPIO.output(M_RIGHT, GPIO.LOW)
                GPIO.output(M_LEFT, GPIO.LOW)
                print('dc = left')
               

            
except KeyboardInterrupt:
    print("Exit pressed Ctrl+C")

finally:
    pwm.stop()
    print("CleanUp")
    GPIO.cleanup()
    print("End of program")
