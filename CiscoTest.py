#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re

class CiscoTest:
	"""
	Chech is it cisco
	"""

	def __init__(self, host):
		self.host = host

	def PrintParams(self):
		print 'Check is cisco:', self.host


	def Check(self):
		p = subprocess.Popen(['./check_cisco.sh', self.host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		#print out
		#print err
		
		# check is it cisco
		m = re.search('\<\+\+\+cisco\+\+\+\>', out)
		if (m):
			return True
		else:
			return False
		
		return 0
