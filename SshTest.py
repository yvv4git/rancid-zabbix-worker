#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko

class SshTest:
	"""
	Класс, который занимается проверкой учетных данных по протоколу ssh
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
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			client.connect(self.host, username=self.login, password=self.password, allow_agent=False, look_for_keys=False, timeout=self.timeout)
			client.close()
			return True
		except:
			return False


'''
c = SshTest('215.12.18.123', 'user', 'xxxxx', 3)
c.GetParams()
c.AckCheck()
'''
