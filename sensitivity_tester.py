# The goal of this script is to find the range that *I* can detect easily on the 4.6kHz piezo devices I am using.

import RPi.GPIO as GPIO
import readchar
import time
import random

def init_gpio(pin, freq) :
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.OUT)
	p = GPIO.PWM(pin, freq)
	p.start(50) #50% duty, makes freq=freq
	return p


def test_freq(pwm, dict, base_freq, compare_freq) :
	key=null
	while key not in ["q", "s", "d"] :
		key=readchar.readkey()
		pwm.ChangeFrequency(base_freq)
		time.sleep(1)
		pwm.ChangeFrequency(compare_freq)
		time.sleep(1)

	if key=='s' : #detected as the same
		insert_freq(dict, base_freq, compare_freq, False)
	elif key=='d' :
		insert_freq(dict, base_freq, compare_freq, False)
	else :
		print("you broke the loop.")


def insert_freq(dict, base_freq, compare_freq, detection_status) :
	if base_freq not in dict :
		dict[base_freq]={True:[], False:[]}
	dict[base_freq][detection_status].append(abs(base_freq-compare_freq))


def get_base_feq(dict, min, max, max_diff) :
	val=random.randrange(min,max)
	for key in dict.keys():
		if abs(val-key)<=max_diff : #if within the range of a previously tested value, just use that value.
			val=key
	return val

def get_compare_freq(dict, base_freq, max_diff) :

	if base_freq in dict : #if this freq has already been used
		success=dict[base_freq][True]
		failiure=dict[base_freq][False]
		if abs(max(failiure)-min(success))<=1 :
			return null #the distinction has been found
		else :
			val=random.randrange(base_freq-max_diff,base_freq+max_diff)
			while (abs(val-base_freq) not in success and abs(val-base_freq) not in failiure) : #This will randomly choose values within the given range unless the value has previously been used.
				val=random.randrange(base_freq-max_diff,base_freq+max_diff)
			return val


def run_tests(pwm, min_freq, max_freq, max_diff) :
	null_counter=0
	freq_log={}

	try :
		while null_counter<int((max_freq-min_freq)/max_diff) :
			base_freq=get_base_feq(freq_log, min_freq, max_freq, max_diff)

			compare_freq=get_compare_freq(freq_log, base_freq, max_diff)

			test_freq(pwm, freq_log, base_freq, compare_freq)
	except KeyboardInterrupt :
		pickle.dump( freq_log, open( "freq_log.p", "wb" ) )

def main():
	pin=12
	freq=250 #starting freq
	min_freq=100
	max_freq=400
	max_diff=20

	pwm=init_gpio(pin, freq)

	run_tests(pwm, min_freq, max_freq, max_diff)

if __name__== "__main__":
  main()

