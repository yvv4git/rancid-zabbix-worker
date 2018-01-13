#!/usr/bin/python
# -*- coding: utf-8

import os
import subprocess
import argparse
import time
import re
import argparse
import threading
import datetime
import logging
from threading import Thread
from BruteLists import BruteLists
from TelnetTclTest import TelnetTclTest
from TelnetCiscoEnableTest import TelnetCiscoEnableTest
from SshTest import SshTest


logging.basicConfig(filename='dumper.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)


class Bruter:
	"""
	Класс, который занимается брут-форсом
	"""
	###
	# Инициализация
	def __init__(self, hosts_list, logins_list, passwords_list, timeout, max_threads):
		self.list_hosts = hosts_list
		self.list_logins = logins_list
		self.list_paswds = passwords_list
		self.timeout = timeout
		self.max_threads = max_threads
		logging.info( 'List hosts: ' + str(self.list_hosts) )
		logging.info( 'List logins: ' + str(self.list_logins) )
		logging.info( 'List password: ' + str(self.list_paswds) )
		logging.info( 'Timeout: ' + str(self.timeout) )
		logging.info( 'Max threads: ' + str(self.max_threads) )
		
		# initialyzation
		self.bl = BruteLists(self.list_hosts, self.list_logins, self.list_paswds) # init brute lists
		self.threadQueue = threading.BoundedSemaphore(value=self.max_threads) # create semafore queue
	
	###
	# BRUTE ALL ACCOUNTS TELNET
	def BruteAcksTelnet(self):
		# проверка - имеется ли данный хост(ip) в списке найденных аккаунтов
		def CheckIsFind(ip_addr):
			list_hosts = []
			for ack in self.bl.list_telnet_acks:
				list_hosts.append(ack[0])
			if (ip_addr in list_hosts):
				return True
			else:
				return False
		#поток, который проверяем учетку
		def ThreadCheckAccount(comb, bl):
			self.threadQueue.acquire() # semafore begin
			# ------------------------------------
			stroka_log = "[%s/%s] [%s %s %s]" % (comb[0], bl.max_count,comb[1], comb[2], comb[3])
			logging.info(stroka_log)
			test = TelnetTclTest(comb[1], comb[2], comb[3], self.timeout)		# create object for test telnet account
			rez = test.AckCheck()												#run procedure check
			#print rez
			if (rez == 1): # dlink
				self.bl.list_telnet_acks.append([comb[1], comb[2], comb[3], ''])
				stroka_log = "[+++DLINK] [%s/%s] [%s %s %s]" % (comb[0], bl.max_count, comb[1], comb[2], comb[3])
				logging.info(stroka_log)
			elif (rez == 2): # cisco
				self.bl.list_telnet_acks.append([comb[1], '', comb[3], ''])
				self.bl.list_hosts_cisco.append(comb[1])		# add ip to cisco host list
				stroka_log = "[+++CISCO] [%s/%s] [%s %s %s]" % (comb[0], bl.max_count, comb[1], comb[2], comb[3])
				logging.info(stroka_log)
			elif (rez == 3): # rwr
				self.bl.list_telnet_acks.append([comb[1], comb[2], comb[3], ''])
				stroka_log = "[+++RWR] [%s/%s] [%s %s %s]" % (comb[0], bl.max_count, comb[1], comb[2], comb[3])
				logging.info(stroka_log)
			else:
				pass
			# ------------------------------------
			self.threadQueue.release() # semafore end
		
		# brute
		i = 1
		for comb in self.bl.list_combs_telnet:
			if not CheckIsFind(comb[1]):											# if this host still not work
				p = threading.Thread(target=ThreadCheckAccount, args=[comb, self.bl])
				p.setDaemon(True)
				p.start()
				while threading.activeCount()>self.max_threads:
					time.sleep(1)
				i += 1
		# wait while all threads are not ended
		while (threading.activeCount()>1):
			logging.info("Please wait by threads ended .. " + str(threading.activeCount()))
			time.sleep(1)
	
	
	###
	# BRUTE CISCO-ENABLE
	def BruteAcksTelnetCiscoEnable(self):
		# проверка - имеется ли данный хост(ip) в списке найденных аккаунтов
		def CheckIsFind(ip_addr):
			list_hosts = []
			for ack in self.bl.list_telnet_acks_cisco_en:
				list_hosts.append(ack[0])
			if ip_addr in list_hosts:
				return True
			else:
				return False
		#поток для брута
		def TreadCheckAccountCiscoEnable(comb, bl):
			self.threadQueue.acquire() # semafore begin
			# ------------------------------------
			stroka_log = "[%s/%s] [%s %s %s]" % (comb[0], bl.max_count, comb[1], comb[2], comb[3])
			logging.info(stroka_log)			
			test_cisco_en = TelnetCiscoEnableTest(comb[1], comb[2], comb[3], self.timeout)
			if test_cisco_en.AckCheck():
				stroka_log = "[+++++CISCO-ENABLE] [%s/%s] [%s %s %s]" % (comb[0], bl.max_count, comb[1], comb[2], comb[3])
				logging.info(stroka_log)
				bl.list_telnet_acks_cisco_en.append([comb[1], comb[2], comb[3]])
			else:
				pass
			#time.sleep(2)
			# ------------------------------------
			self.threadQueue.release() # semafore end
		
		i = 1
		for comb in self.bl.list_combs_cisco:
			if not CheckIsFind(comb[1]):											# if this host still not work
				p = threading.Thread(target=TreadCheckAccountCiscoEnable, args=[comb, self.bl])
				p.setDaemon(True)
				p.start()
				while threading.activeCount()>self.max_threads:
					time.sleep(1)
				i += 1
			
		while (threading.activeCount()>1):
			stroka_log = "Please wait by threads ended .. ", threading.activeCount()
			logging.info(stroka_log)
			time.sleep(1)
		
		#self.bl.AddCiscoEnable2Acks() # add cisco acks to list_all_acks
	
	
	###
	# BRUTE SSH ACCOUNT
	def BruteAcksSsh(self):
		# проверка - имеется ли данный хост(ip) в списке найденных аккаунтов
		def CheckIsFind(ip_addr):
			list_hosts = []
			for ack in self.bl.list_ssh_acks:
				list_hosts.append(ack[0])
			if ip_addr in list_hosts:
				return True
			else:
				return False
		# тестим учетку в потоке
		def ThreadCheckAccountSsh(comb, bl):
			self.threadQueue.acquire() # semafore begin
			# ------------------------------------
			stroka_log = "[%s/%s] [%s %s %s]" % (comb[0], bl.max_count, comb[1], comb[2], comb[3])
			logging.info(stroka_log)
			test_ssh = SshTest(comb[1], comb[2], comb[3], self.timeout)
			if (test_ssh.AckCheck()):
				bl.list_ssh_acks.append([comb[1], comb[2], comb[3], ''])
				stroka_log = "[+++SSH] [%s/%s] [%s %s %s]" % (comb[0], bl.max_count, comb[1], comb[2], comb[3])
				logging.info(stroka_log)
			else:
				pass
			# ------------------------------------
			self.threadQueue.release() # semafore end
	
	
		i = 1
		for comb in self.bl.list_combs_ssh:
			if not CheckIsFind(comb[1]):								# if this host still not work
				p = threading.Thread(target=ThreadCheckAccountSsh, args=[comb, self.bl])
				p.setDaemon(True)
				p.start()
				while threading.activeCount()>self.max_threads:
					time.sleep(1)
	
	###
	# Сохранить результаты в файл формата rancid .cloginrc
	def Save4Rancid(self, f_name, list_add):
		try:
			f = open(f_name, 'a')
			for ack in list_add:
				if (ack[1] == ''): # this is cisco
					f.write("add password\t%s\t%s\t%s\n" % (ack[0], ack[2], ack[3]))
				else:
					f.write("add user\t%s\t%s\n" % (ack[0], ack[1]))
					f.write("add password\t%s\t%s\n" % (ack[0], ack[2]))
			f.close()
			#return True
		except:
			#return False
			logging.info("[-] SOME ERRORS WITH SAVE RANCID FILE")
		
	
	###
	# Сохранить в файл списко хостов, к которым учетки подобрать не удалось
	def AddNoFind(self, f_name):
		logging.info("Save no-find: " + str(f_name))
		f = open(f_name, 'a')
		for h in self.bl.list_nofind:
			f.write("%s\n" % h)
			logging.info("No-find host save to file: " + h)
		f.close()

