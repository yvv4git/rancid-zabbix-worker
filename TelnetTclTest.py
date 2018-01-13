#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re

class TelnetTclTest:
	"""
	This code check account by special tcl script
	"""

	def __init__(self, host, login, password, time_out):
		self.host = host
		self.login = login
		self.password = password
		self.timeout = time_out

	def GetParams(self):
		print self.host
		print self.login
		print self.password
		print self.timeout


	def AckCheck(self):
		#print "\n====> ", self.login, self.password
		p = subprocess.Popen(['./probe_telnet.sh', self.host, self.login, self.password, str(self.timeout)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		#print self.host, self.login, self.password
		out, err = p.communicate()
		#print out
		
		# dlink
		m = re.search('\<\+\+\+dlink\+\+\+\>', out)
		if (m):
			return 1
		
		# cisco
		m = re.search('\<\+\+\+cisco\+\+\+\>', out)
		if (m):
			return 2
		
		# rwr
		m = re.search('\<\+\+\+rwr\+\+\+\>', out)
		if (m):
			return 3
		
		return 0


