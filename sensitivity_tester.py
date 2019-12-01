# The goal of this script is to find the range that *I* can detect easily on the 4.6kHz piezo devices I am using.

import RPi.GPIO as GPIO
import readchar
import termios
import time
import random
import pickle
import sys
import tty
import select

import matplotlib.pyplot as plt


def init_gpio(pin, freq) :
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.OUT)
	p = GPIO.PWM(pin, freq)
	p.start(50) #50% duty, makes freq=freq
	return p

def isData(): #https://stackoverflow.com/a/2409034
	return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def test_freq(pwm, dict, base_freq, compare_freq) :
	key=None

	print("diff= ", abs(base_freq-compare_freq))
	old_settings = termios.tcgetattr(sys.stdin)
	try:
		tty.setcbreak(sys.stdin.fileno())

		while True:
			pwm.ChangeFrequency(base_freq)
			print(base_freq)
			time.sleep(1)
			pwm.ChangeFrequency(compare_freq)
			print(compare_freq)
			time.sleep(1)

			if isData():
				key = sys.stdin.read(1)
				if key in ["q", "s", "d"]:
					break

	finally:
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


	if key=='s' : #detected as the same
		insert_freq(dict, base_freq, compare_freq, False)
		print("same")
	elif key=='d' :
		insert_freq(dict, base_freq, compare_freq, True)
		print("different")

	else :
		print("you broke the loop.")

#inserts freq data
def insert_freq(dict, base_freq, compare_freq, detection_status) :
	if base_freq not in dict :
		dict[base_freq]={True:[], False:[]}
	dict[base_freq][detection_status].append(abs(base_freq-compare_freq))
	print(dict)

#selects a base_freq
def get_base_feq(dict, min, max, max_diff) :
	val=random.randrange(min,max)
	for key in dict.keys():
		if abs(val-key)<=max_diff : #if within the range of a previously tested value, just use that value.
			val=key
	return val


#generates a frequency from the base_freq
def get_compare_freq(dict, base_freq, max_diff) :
	compare_freq=None
	if base_freq in dict : #if this freq has already been used
		success=dict[base_freq][True]
		failiure=dict[base_freq][False]

		if  len(failiure)>0 :
			if len(success)>0 and (abs(max(failiure)-min(success))<=1) :
				compare_freq=None #the distinction has been found
			else : #This should ensure values below the sense level do not keep popping up
				print("there is a same, there is no diff or diff and same are not too close")
				diff=random.randrange(max(failiure),max_diff)
				compare_freq=base_freq+(1 if random.random() < 0.5 else -1)*diff

		else :
			print("loop case")
			val=random.randrange(base_freq-max_diff,base_freq+max_diff)
			while (abs(val-base_freq) not in success and abs(val-base_freq) not in failiure) : #This will randomly choose values within the given range unless the value has previously been used.
				val=random.randrange(base_freq-max_diff,base_freq+max_diff)
			compare_freq=val
	else :
		print("first value for entry")
		compare_freq=random.randrange(base_freq-max_diff,base_freq+max_diff)

	return compare_freq


def run_tests(pwm, min_freq, max_freq, max_diff) :
	None_counter=0
	freq_log={}
	print("starting tests")
	num_vals=int((max_freq-min_freq)/max_diff)
	print("num_vals ", num_vals)

	try :
		while None_counter<num_vals :
			base_freq=get_base_feq(freq_log, min_freq, max_freq, max_diff)

			compare_freq=get_compare_freq(freq_log, base_freq, max_diff)
			if compare_freq==None :
				None_counter+=1
				print("already completed")
			else :
				test_freq(pwm, freq_log, base_freq, compare_freq)
	except KeyboardInterrupt :
		print("broke")
	pickle.dump( freq_log, open( "freq_log.p", "wb" ) )
	plot_data(freq_log)


def plot_data(dict) :
	for key in dict.keys() :
		plt.scatter(key, min(dict[key][True]), c="blue")
		plt.scatter(key, max(dict[key][False]), c="red")

def main():
	pin=12
	freq=250 #starting freq
	min_freq=150 #the min and max vals are determined by the range finding script
	max_freq=350
	max_diff=50

	pwm=init_gpio(pin, freq)
	print("initialized")
	run_tests(pwm, min_freq, max_freq, max_diff)

if __name__== "__main__":
  main()
