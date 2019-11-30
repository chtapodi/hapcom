# The goal of this script is to find the range that *I* can detect easily on the 4.6kHz piezo devices I am using.

import RPi.GPIO as GPIO
import readchar
import time


freq=250#4600
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, freq)
p.start(50)

step=5
print("starting")
while True :
	try :
		key=readchar.readkey()
		print("key= ", key)
		if key=='w' :
			freq+=step
		elif key=='s' :
			freq-=step
		else :
			break
		print("freq: ", freq)
		p.ChangeFrequency(freq)
		time.sleep(.1)
	except KeyboardInterrupt:
		pass


# p.stop()
# GPIO.cleanup()
