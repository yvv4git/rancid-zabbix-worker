#!/usr/bin/python
# -*- coding: utf-8

import os
import time
#import ntpath
import socket
import logging
from CiscoTest import CiscoTest


logging.basicConfig(filename='dumper.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)

class DevCheck:
	def __init__(self):
		self.list_hosts = []
		self.list_telnet = []
		self.list_ssh = []
		self.list_blocked = []
		self.list_telnet_cisco = []
		self.list_telnet_nocisco = []
	
	def OpenDbFile2List(self, file_name):
		try:
			list_tmp = open(file_name, "r").readlines() #self.list_hosts
			for l in list_tmp:
				pos = l.find(':')
				ip_addr = l[:pos]
				if (ip_addr.find('#') == -1):
					self.list_hosts.append(ip_addr) # add ip address
				#print l[:pos]
		except(IOError): 
			#print "Error: Check your file hosts-list path: ", self.file_hosts
			pass
			
	def OpenFile2List(self, file_name):
		list_tmp = open(file_name, "r").readlines() #self.list_hosts
		for l in list_tmp:
			self.list_hosts.append(l[:-1])
	
	def CheckTcpPorts(self):
		
		def CheckTelnet(host):
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = sock.connect_ex((host, 23))
			if result == 0:
				return True
			else:
				return False
				
		def CheckSsh(host):
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = sock.connect_ex((host, 22))
			if result == 0:
				return True
			else:
				return False
				
		for ip_addr in self.list_hosts:
			#print ip_addr
			if (CheckTelnet(ip_addr)):
				#print ip_addr, 'is telnet'
				self.list_telnet.append(ip_addr)
			elif(CheckSsh(ip_addr)):
				#print ip_addr, 'is ssh'
				self.list_ssh.append(ip_addr)
			else:
				#print ip_addr, 'is BLOCKED'
				self.list_blocked.append(ip_addr)
	
	def CheckCisco(self):
		for l in self.list_telnet:
			ct = CiscoTest(l)
			#ct.PrintParams()
			if ct.Check():
				#print "Check is cisco:", l, ' +'
				self.list_telnet_cisco.append(l)
			else:
				#print "Check is cisco:", l, ' -'
				pass
	
	def DelCiscoFromList(self):
		for t in self.list_telnet:
			if t not in self.list_telnet_cisco:
				self.list_telnet_nocisco.append(t)
	
	def PrintLists(self):
		#print "\nLIST TELNET:"
		for l in self.list_telnet:
			#print l
			pass
		#print "\nLIST SSH:"
		for l in self.list_ssh:
			#print l
			pass
		#print "\nLIST BLOCKED:"
		for l in self.list_blocked:
			#print l
			pass
	
	def GetLists(self):
		return self.list_telnet_cisco, self.list_telnet_nocisco, self.list_ssh, self.list_blocked
'''
dc = DevCheck()
dc.OpenFile2List('test_ip.lst')
dc.CheckTcpPorts()
dc.PrintLists()
'''
'''
dc = DevCheck()
dc.OpenDbFile2List('/var/lib/rancid/SPb_cisco/router.db')

print "\n[*] CHECK PORTS"
dc.CheckTcpPorts()

print "\n[*] PRINT LISTS"
dc.PrintLists()

print "\n[*] CHECK TELNET FOR CISCO"
dc.CheckCisco()
dc.DelCiscoFromList

print "\n[*] LIST CISCO:"
for l in self.list_telnet_cisco:
	print l
print "\n[*] LIST NO CISCO CISCO:"
for l in self.list_telnet_nocisco:
	print l
'''
