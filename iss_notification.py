#!/usr/bin/env python

# iss_notification.py
# ------------------- 
#
# Version 0.1, February 2014
#
# Display upcoming passes of the International Space Station using the
# open source OpenNotify API at http://api.open-notify.org. Optionally,
# output status information over a serial port for physical notifications
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
# The OpenNotify API is copyright Nathan Bergey (@natronics)
#
# Tested:   python v2.7.5
# Requires: python-enum34

import sys
import time
import serial
import getopt
import requests

from enum import Enum

iss_states = {
		'RECEDING' 	: ( 2700, 120 ),
		'APPROACHING' 	: ( 900,  60  ),
		'CLOSING' 	: ( 300,  30  ),
		'INCOMING' 	: ( 60,   15  ),
		'IMMINENT' 	: ( 0,    5   )
	     }	


class Leds():
	"""Facilitates physical notifications of upcoming ISS passes by communicating to a serial attached arduino"""
	
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
	
class NotifyAPI():
	"""Uses the API at http://api.open-notify.org to retrieve upcoming ISS passes for a given longitude/latitude"""
	
	url="http://api.open-notify.org/iss-pass.json"
	#url="http://192.168.1.1:5000/iss-pass.json"	# If using local instance of open-notify API

	# Constructor
	def __init__(self, params):
		self.params = params

	# Retrieve passes from the API service 
	def getPassData(self):
		try:
			response = requests.get(self.url, params=self.params)
			passes = {}

			if ((response.json()).get('message') == 'success'):
				passes = response.json()

			return passes
		except requests.exceptions.ConnectionError:
			print '\nERROR: Failed to retrieve URL:',self.url,'\n'
			sys.exit(8)
		except Exception:
			print '\nERROR: An unknown error occurred!\n' 
			sys.exit(9)

def usage():
	print ''
	print 'Usage:'
	print '\t', sys.argv[0], "-t <latitude> -n <longitude> [-a <altitude>] [-p <passes] [-s <port>] [-q] [-h]" 
	print ''
	print 'Where:'
	print '\t-t, --latitude <latitude>\t:\tThe latitude of the location to retrieve passes for'
	print '\t-n, --longitude <longitude>\t:\tThe longitude of the location to retrieve passes for'
	print '\t-a, --altitude <altitude>\t:\tThe altitude of the location to retrieve passes for (default: 1)'
	print '\t-p, --passes <passes>\t\t:\tRetrieve the next <passes> number of passes (default: 1)'
	print '\t-s, --serial <port>\t\t:\tUse the specified serial port to indicate a pass'
	print '\t-q, --quiet\t\t\t:\tQuiet mode. Do not output any retrieved pass information to the console'
	print '\t-h, --help\t\t\t:\tDisplay this message'
	print ''

def main(argv):
	try:
		# default values
		params = {'lat' : -999,
			  'lon' : -999,
			  'alt' : 1,
			  'n'	: 1}

		quiet  = False
		serial = False
	
		serial_port = '/dev/ttyUSB0'

		try:
			opts, args = getopt.getopt(argv,"hqt:n:a:p:s:",["help","quiet","latitude=","longitude=","altitude=","passes=", "serial="])
   		except getopt.GetoptError:
			print '\nERROR: Incorrect options specified!\n'
      			usage()
      			sys.exit(1)
		
		try:
			for opt, arg in opts:
      				if opt in ("-h", "--help"):
					usage()
		         		sys.exit(0)
		      		elif opt in ("-t", "--latitude"):
		         		params['lat'] = float(arg)
		      		elif opt in ("-n", "--longitude"):
		         		params['lon'] = float(arg)
		      		elif opt in ("-a", "--altitude"):
		         		params['alt'] = int(arg)
		      		elif opt in ("-p", "--passes"):
		         		params['n'] = int(arg)
		      		elif opt in ("-s", "--serial"):
					serial = True
					serial_port = arg
		      		elif opt in ("-q", "--quiet"):
		         		quiet = True	
		except ValueError:
			print '\nERROR: Specified options should be in numeric format!\n'
			sys.exit(2)

		# Check arguments are within correct bounds for the open-notify API
		if ((params['lat'] == -999) | (params['lon'] == -999)):
			print '\nERROR: You must specify both a latitude and a longitude!\n'
			sys.exit(3)
		elif ((params['lat'] < -80) | (params['lat'] > 80)):
			print '\nERROR: Latitude must be between -80.0 and 80.0 degrees!\n'
			sys.exit(4)
		elif ((params['lon'] < -180) | (params['lon'] > 180)):
			print '\nERROR: Longitude must be between -180.0 and 180.0 degrees!\n'
			sys.exit(5)
		elif ((params['alt'] < 0) | (params['alt'] > 10000)):
			print '\nERROR: Altitude must be between 1 and 10,000 metres!\n'
			sys.exit(6)
		elif ((params['n'] < 1) | (params['n'] > 100)):
			print '\nERROR: Passes must be between 1 and 100!\n'
			sys.exit(7)
	
		# Main execution
		napi = NotifyAPI(params)
		if(serial):
			leds = Leds()
			serial = leds.setup(serial_port)
	
		next_pass = {}
		last_pass = {}
	
		last_state = Leds.State.TEST
		curr_state = Leds.State.RECEDING
	
		update_freq = iss_states.get('RECEDING')[1]
	
		if(not quiet):
			print ''
			print 'ISS Notifcations'
			print '================'
			print ''
			
			if(serial):
				print 'Using serial port:', serial_port, '- testing. Wait 5 seconds.'
				print ''

				leds.sendState(Leds.State.TEST)
				time.sleep(5)
	
			print '-----------------------------------------------------'
	
		while True:
			pass_data = napi.getPassData()
	
			if (len(pass_data) > 0):
				passes = pass_data.get('response')
	
				if(len(passes) == params.get('n')):
					next_pass = passes[0]
	
					currtime = int(time.time())
					difftime = int(next_pass.get('risetime') - currtime)
	
					if((difftime < 0)):
						if(len(last_pass) == 0):
							update_freq = 600
						else:
       	                         			update_freq = last_pass.get('duration')
 		                               		curr_state = Leds.State.OVERHEAD
					else:
	
						if(difftime > iss_states.get('RECEDING')[0]):
							update_freq = iss_states.get('RECEDING')[1]
							curr_state = Leds.State.RECEDING
						elif((difftime <= iss_states.get('RECEDING')[0]) & (difftime > iss_states.get('APPROACHING')[0])):
							update_freq = iss_states.get('APPROACHING')[1]
							curr_state = Leds.State.APPROACHING
						elif((difftime <= iss_states.get('APPROACHING')[0]) & (difftime > iss_states.get('CLOSING')[0])):
							update_freq = iss_states.get('CLOSING')[1]
							curr_state = Leds.State.CLOSING
						elif((difftime <= iss_states.get('CLOSING')[0]) & (difftime > iss_states.get('INCOMING')[0])):
							update_freq = iss_states.get('INCOMING')[1]
							curr_state = Leds.State.INCOMING
						elif((difftime <= iss_states.get('INCOMING')[0]) & (difftime > iss_states.get('IMMINENT')[0])):
							update_freq = iss_states.get('IMMINENT')[1]
							curr_state = Leds.State.IMMINENT
	
						last_pass = next_pass
	
					# Just print the list of retrieved passes
					if(not quiet):
						if(difftime < 0):
							print ''
							print 'ISS is currently overhead!'
							print ''
							print '-----------------------------------------------------'
	
						for idx, iss_pass in enumerate(passes, start=1):
							print ''
							print 'Pass #' + str(idx) + ':'
							print ''
							print 'Current time (Local):\t', time.asctime()
							print 'Pass time (Local):\t',time.ctime(iss_pass.get('risetime'))
							print 'Pass time (UTC):\t', time.asctime(time.gmtime(iss_pass.get('risetime')))
							print 'Duration:\t\t', iss_pass.get('duration'), 'seconds'
							print 'Difference:\t\t', (iss_pass.get('risetime') - int(time.time())), 'seconds'
							print 'Update:\t\t\t', update_freq, 'seconds'
							print ''
							print '-----------------------------------------------------'

					if(last_state != curr_state):
						last_state = curr_state

						if(serial):
							leds.sendState(curr_state)
	
					time.sleep(update_freq)
				else:
					# If the ISS was overhead, finish the pass as this is expected behaviour
				        if(curr_state == Leds.State.OVERHEAD):
						curr_state = Leds.State.RECEDING
                                                last_state = curr_state

                                                if(serial):
                                                        leds.sendState(curr_state)

					if(not quiet):
                                        	print ''
                                        	print 'WARNING: Incorrect number of passes retrieved!'
						print ''
						print 'Retry in 10 seconds'
                                        	print ''
                                        	print '-----------------------------------------------------'

					time.sleep(10)
					
			else:
				if(not quiet):
					print ''
					print 'WARNING: Failed to retrive pass data!'
					print ''
					print '-----------------------------------------------------'
	except KeyboardInterrupt:
		if(serial):
			leds.close(serial_port)

		print '\nExiting.'
		sys.exit()
	
if __name__ == '__main__':
	main(sys.argv[1:])
