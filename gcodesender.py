#!/usr/bin/python
"""
Simple g-code streaming script
"""
 
import serial
import time
import argparse
from threading import Thread, Event
from template_matching import FilamentDetector


def removeComment(string):
	if (string.find(';')==-1):
		return string
	else:
		return string[:string.index(';')]
 
def initialize():
	# Open serial port
	#s = serial.Serial('/dev/ttyACM0',115200)
	s = serial.Serial(args.port,115200)
	print('Opening Serial Port')
	
	# Open g-code file
	#f = open('/media/UNTITLED/shoulder.g','r');
	f = open(args.file,'r');
	print('Opening gcode file')
	
	# Wake up 
	s.write('\r\n\r\n') # Hit enter a few times to wake the Printrbot
	time.sleep(2)   # Wait for Printrbot to initialize
	s.flushInput()  # Flush startup text in serial input
	print('Sending gcode')
	return (f,s)

def task(f, s):	
	# Stream g-code
	global response
	for code_num, line in enumerate(f):
		if response == 1:
			l = removeComment(line)
			l = l.strip() # Strip all EOL characters for streaming
			if  (l.isspace()==False and len(l)>0) :
				print('Sending: ' + l)
				s.write(l + '\n') # Send g-code block
				grbl_out = s.readline() # Wait for response with carriage return
				print(' : ' + grbl_out.strip())
		elif response == 0:
			print('Stopped')
			break
		elif response == 2:
			print('Paused')
			response = int(input())
			if response == 3:
				# s.close()
				# s = serial.Serial('/dev/ttyUSB0', 115200)
				# time.sleep(2)
				command = raw_input('Enter the manual Gcode: ')
				command = command.strip()
				if(command.isspace()==False and len(command)>0):
					print('Sending ' + command)
					s.write(command + '\n')
					grbl_out = s.readline()
					print(' : ' + grbl_out.strip())
			elif response == 4:
				print('Resumed')
				response = 1
			else:
				print('Invalid option')
				response = 2


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='This is a basic gcode sender.')
	parser.add_argument('-i','--input',help='Input image filepath',required=True)
	parser.add_argument('-p','--port',help='Input USB port',required=True)
	parser.add_argument('-f','--file',help='Gcode file path',required=True)
	args = parser.parse_args()

	fd = FilamentDetector()
	# show values ##
	print ("USB Port: %s"%(args.port))
	print ("Gcode file: %s"%(args.file))
	print ("Image gile: %s"%(args.input))

	gcode_file, s = initialize()
	
	event = Event()
	response = 1
	thread1 = Thread(name='Gcode-Sender-Thread', target=task, args=(gcode_file, s)).start()
	time.sleep(10)

	response = fd.process(args.input)
	print('Main Thread Running')

	if response == 0:
		# Close file and serial port
		f.close()
		s.close()
