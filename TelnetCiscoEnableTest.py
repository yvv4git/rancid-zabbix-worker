#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re

class TelnetCiscoEnableTest:
	"""
	Chech cisco-enable password
	"""

	def __init__(self, host, password, password_enable, time_out):
		self.host = host
		self.password = password
		self.password_enable = password_enable
		self.timeout = time_out

	def GetParams(self):
		print 'HOST:', self.host
		print 'PASSWORD:', self.password
		print 'PASSWORD-ENABLE:', self.password_enable
		print 'TIMEOUT:', self.timeout


	def AckCheck(self):
		p = subprocess.Popen(['./probe_cisco_enable.sh', self.host, self.password, self.password_enable, str(self.timeout)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		#print out
		#print err
		
		# cisco
		m = re.search('\<\+\+\+\+\+\>', out)
		if (m):
			return True
		else:
			return False
		
		return 0


#c = TelnetCiscoEnableTest('79.175.22.253', 'Gtr%vkl2#', "Th76salk$#@", 2)
#c.GetParams()
#if c.AckCheck():
#	print "YES"
#else:
#	print "NO"
