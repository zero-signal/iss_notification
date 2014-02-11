#!/usr/bin/env python

# led_test.py
# -----------
#
# Version 0.1, February 2014
#
# Output commands over a serial port for testing LED strips controlled
# using an Arduino and IR LED.
#
# Copyright (C) 2014 - Zerosignal (zerosignal1982@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Tested:   python v2.7.5
# Requires: python-enum34

import sys
import time
import serial
import getopt

from enum import Enum

class Leds():
	"""A class that encapsulates functionality required to control RGB LED strips via and serially connected arduino"""
	
	cmd_delim_begin  = 0x24		# $ - Command start
	cmd_delim_end    = 0x21		# ! - Command end

	configured	 = False

	class State(Enum):
                RECEDING      	= 0x41	# 'A'
                APPROACHING   	= 0x42	# 'B'
                CLOSING       	= 0x43  # 'C'
                INCOMING      	= 0x44	# 'D'
                IMMINENT      	= 0x45	# 'E'
                OVERHEAD      	= 0x46  # 'F'
		TEST 		= 0x5A	# 'Z'

	def __init__(self):
		pass

	def setup(self,device):
		self.device = device
	
	        try:
                        self.ser = serial.Serial(self.device, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None)

			if(self.ser.isOpen()):
				self.ser.close()

                       	self.ser.open()
			self.configured = True
                except serial.serialutil.SerialException as se:
                        print '\nERROR: Serial support disabled. Unable to open serial port,', self.device, ':', se.message
			self.configured = False

		return self.configured

	def close(self,device):
	        try:
			if(self.ser.isOpen()):
				self.ser.close()
                except serial.serialutil.SerialException as se:
                        print '\nERROR: Unable to close serial port,', self.device, ':', se.message

	def sendState(self, state):
		error = False

		if(self.configured):
			cmd = bytearray()

			cmd.append(self.cmd_delim_begin)
			cmd.append(state.value)
			cmd.append(self.cmd_delim_end)

			try:
				self.ser.write(cmd)
			except serial.serialutil.SerialException as se:
				print '\nERROR: Unable to send serial data using port,', self.device, ':', se.message
				error = True

		return error
	
def usage():
	print ''
	print 'Usage:'
	print '\t', sys.argv[0], "-s <port> [-t <seconds>] [-h]" 
	print ''
	print 'Where:'
	print '\t-s, --serial <port>\t\t:\tUse the specified serial port to indicate a pass'
	print '\t-t, --time <seconds>\t\t:\tDelay time between sending commmands. Defaults to 10s.'
	print '\t-h, --help\t\t\t:\tDisplay this message'
	print ''

def main(argv):
	try:
		serial = False
		serial_port = '/dev/ttyUSB0'

		sleep_time = 10

		try:
			opts, args = getopt.getopt(argv,"hs:t:",["help", "serial=", "time="])
   		except getopt.GetoptError:
			print '\nERROR: Incorrect options specified!\n'
      			usage()
      			sys.exit(1)

		try:
		
			for opt, arg in opts:
      				if opt in ("-h", "--help"):
					usage()
	       		  		sys.exit(0)
	      			elif opt in ("-s", "--serial"):
					serial = True
					serial_port = arg
				elif opt in ("-t", "--time"):
					sleep_time = int(arg)
		except ValueError:
                        print '\nERROR: Specified options should be in numeric format!\n'
                        sys.exit(2)


		if(serial):
			leds = Leds()
			serial = leds.setup(serial_port)

			print ''
			print 'Sleep time between commands is:', sleep_time, 'seconds'
			print ''

			for state in Leds.State:
				print 'Sending:', state
				time.sleep(sleep_time)

				leds.sendState(state)

			print ''
		else:
			print ''
			print 'You must specify a serial port. Exiting'
			print ''

			sys.exit(1)
	

	except KeyboardInterrupt:
		if(serial):
			leds.close(serial_port)

		print '\nExiting.'
		sys.exit()
	
if __name__ == '__main__':
	main(sys.argv[1:])
