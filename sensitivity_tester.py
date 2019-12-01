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
	old_settings = termios.tcgetattr(sys.stdin)
	try:
		tty.setcbreak(sys.stdin.fileno())

		while True:
			pwm.ChangeFrequency(base_freq)
			# print(base_freq)
			time.sleep(1)
			pwm.ChangeFrequency(compare_freq)
			# print(compare_freq)
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

#selects a base_freq
def get_base_feq(dict, min, max, max_diff) :
	val=random.randrange(min,max)
	for key in dict.keys():
		if abs(val-key)<=max_diff : #if within the range of a previously tested value, just use that value.
			val=key
	return val

def get_compare_freq(dict, base_freq, max_diff) :
	# print("get freq")
	diff=-1
	if base_freq in dict : #if this freq has already been used
		print(base_freq, ":", dict[base_freq])
		success=dict[base_freq][True]
		failiure=dict[base_freq][False]

		if len(failiure)>0 or len(success)>0 :
			while diff in success or diff in failiure or diff==-1 :
				# print("loop")
				if len(failiure)>0 and len(success)>0 : #if there are entries in both
					if (abs(max(failiure)-min(success))<=1) :
						# print("returned none")
						return None #the distinction has been found
					else :
						#narrowing in on where the distinction is
						# print("narrowing")
						diff=random.randrange(max(failiure),min(success))

				elif len(failiure)>0 : #If there have only been failiures
					#This should generate a random value within the range but avoiding values less than the "same" cutoff
					diff=random.randrange(max(failiure),max_diff)
					# print("fail diff= ", diff)
				else : #If there have only been failiures
					#This should generate a random value within the range but avoiding values less than the "same" cutoff
					diff=random.randrange(0,min(success))
					# print("succ diff= ", diff)



	else :
		# print("first value for entry")
		diff=random.randrange(0,max_diff)
	# print("final_diff ", diff)
	compare_freq=base_freq+(1 if random.random() < 0.5 else -1)*diff
	return compare_freq




def run_tests(pwm, min_freq, max_freq, max_diff) :
	None_counter=0
	completed_freqs=[]
	freq_log={}
	print("starting tests")
	num_vals=int((max_freq-min_freq)/max_diff)
	print("num_vals ", num_vals)

	try :
		while None_counter<num_vals :
			base_freq=get_base_feq(freq_log, min_freq, max_freq, max_diff)
			if base_freq not in completed_freqs :
				compare_freq=get_compare_freq(freq_log, base_freq, max_diff)
				if compare_freq==None :
					None_counter+=1
					completed_freqs.append(base_freq)
					# print("already completed")
				else :
					test_freq(pwm, freq_log, base_freq, compare_freq)
	except KeyboardInterrupt :
		print("broke")
	pickle.dump( freq_log, open( "freq_log.p", "wb" ) )
	plot_data(freq_log)


def plot_data(dict) :
	selected=[]
	for key in dict :
		print("key ", dict[key][True])
		success=dict[key][True]
		failiure=dict[key][False]
		selected.append(max(success))
		for point in success :
			plt.scatter(key, point, c="blue")
		for point in failiure :
			plt.scatter(key, point, c="red")
	plt.savefig('collected_data.png')

def main():
	pin=12
	freq=250 #starting freq
	min_freq=150 #the min and max vals are determined by the range finding script
	max_freq=350
	max_diff=100

	pwm=init_gpio(pin, freq)
	print("initialized")
	run_tests(pwm, min_freq, max_freq, max_diff)

if __name__== "__main__":
  main()
