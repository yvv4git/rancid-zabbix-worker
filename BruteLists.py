#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import time
import os
import re
import logging
from DevCheck import DevCheck

logging.basicConfig(filename='dumper.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)

class BruteLists:
	"""
	Данный класс хранит текущие настройки, переданные программе после запуска и параметры
	работы программы в процессе. Например список хостов, список хостов с подобранными паролями и т.д.
	"""
	###
	# Инициализация
	def __init__(self, list_hosts, list_logins, list_paswds):
		self.list_hosts = list_hosts # изначально все хосты загружаются в этот список
		self.list_logins = list_logins
		self.list_paswds = list_paswds
		
		self.list_hosts_telnet = []	# список хосов, которые доступны только по telnet
		self.list_hosts_ssh = []	# список хосов, которые доступны только по ssh
		
		self.list_combs_telnet = []
		self.list_combs_ssh = []
		
		self.cloginrc = '/home/admin/.cloginrc'
		
		self.list_telnet_acks = []	# сбрученные аккаунты telnet
		self.list_ssh_acks = []		# сбрученные аккаунты ssh
		self.list_nofind = []		# хосты, к которым не удалось подобрать учетку
		
		self.list_hosts_cisco = [] # если это циско, то добавляем в этот список для того, чтобы брутить отдельно на cisco-enable
		self.list_combs_cisco = []	# комбинации для брута cisco-enable
		self.list_telnet_acks_cisco_en = [] # сбрученные аккаунты telnet для циско-enable
		
		self.max_count = 0		# используем как счетчик
		
		# чистим списки. Удаляем хосты, которые уже есть в /home/admin/.cloginrc
		logging.info( 'Count host list before cleaning: ' + str(len(self.list_hosts)) )
		self.Del_AcksCloginrc()
		logging.info( 'Count host list after cleaning: ' + str(len(self.list_hosts)) )
		
		# получаем списки хостов telnet & ssh
		self.list_hosts_telnet, self.list_hosts_ssh = self.Parse_tcp(self.list_hosts)
		
		# заполняем списки комбинаций для telnet & ssh
		self.list_combs_telnet = self.Set_Combs(self.list_hosts_telnet, self.list_logins, self.list_paswds)
		self.list_combs_ssh = self.Set_Combs(self.list_hosts_ssh, self.list_logins, self.list_paswds)
		
		
	
	
	###
	# Разбираем хосты на telnet и ssh
	def Parse_tcp(self, list_hosts):
		logging.info( 'Parse ports by protocols: telnet and ssh ' )
		dc = DevCheck()
		dc.list_hosts = list_hosts
		dc.CheckTcpPorts()
		dc.PrintLists()
		#
		return dc.list_telnet, dc.list_ssh
	
	
	###
	# Заполнить список всех возможных комбинаций
	def Set_Combs(self, list_hosts, list_logins, list_paswds):
		list_rez = []
		i = 1
		for h in list_hosts:
			for l in list_logins:
				for p in list_paswds:
					list_rez.append([i, h, l, p])
					i += 1
		return list_rez
	
	
	###
	# Заполнить список всех возможных комбинаций для подбора cisco-enable
	def Set_Combs_Cisco(self):
		def FindPaswd(ip_addr):
			for ack in self.list_telnet_acks:
				if (ip_addr == ack[0]):
					return ack[2]
			return None
		i = 1
		for c in self.list_hosts_cisco:
			paswd_enter = FindPaswd(c)
			#print "PENTER:", paswd_enter
			for p in self.list_paswds:
				#print "+++>", c, paswd_enter, p
				self.list_combs_cisco.append([i, c, paswd_enter, p])
				i += 1
				
	
	
	###
	# Удалить из списка list_hosts те хосты, которые фигурируют в файле с известными учетками .cloginrc
	def Del_AcksCloginrc(self):
		# Прочитать cloginrc файл с аккаунтами, чтобы оставить только те аккаунты, которые не известны
		def ReadCloginrc(f_name):
			if not os.path.exists(f_name):
				return None
			f = open(f_name, 'r')
			lines = f.readlines()
			f.close()
			
			lines2 = []
			for l in lines:
				re.sub( '\s+', '\t', l ).strip()
				lines2.append(l)
			
			list_ipaddrs = []
			for l in lines2:
				lsplit = l.split('\t')
				if len(lsplit)>=3:
					list_ipaddrs.append(lsplit[1])
			
			lines_rez = []
			for ipa in self.list_hosts:
				if ipa not in list_ipaddrs:
					lines_rez.append(ipa)
			
			#print lines_rez
			self.list_hosts = lines_rez
			
		ReadCloginrc(self.cloginrc)
	
	
	###
	# Заполняем список паролей для хостов паролями для enabled для хостов cisco
	def Add_CiscoEnable2Acks(self):
		if len(self.list_telnet_acks_cisco_en)>0:
			for a_ce in self.list_telnet_acks_cisco_en:
				for a_t in self.list_telnet_acks:
					if (a_ce[0] == a_t[0]):
						#print a, a0
						a_t[3] = a_ce[2]		# в изначальном листе аккаунтоа lisb_ack меняем последний параметр(paswd for cisco enable) на новый из списка подобранных hosts_ack_cisco_en
	
	
	###
	# После брута можно вычислить хосты, к которым не удалось подобрать учетки
	def Find_NoFind(self):
		# заполняем список hosts_find хостами, у которых удалось найти учетку
		hosts_find = []
		for h_find in self.list_telnet_acks:
			hosts_find.append(h_find[0])
		for h_find in self.list_ssh_acks:
			hosts_find.append(h_find[0])
		logging.info( 'List telnet acks: ' + str(self.list_telnet_acks) )
		logging.info( 'List ssh acks: ' + str(self.list_ssh_acks ) )
		logging.info( 'Host find: ' + str(hosts_find) )
		
		
		# перебираем все хосты
		for h in self.list_hosts:
			y_n = False
			
			for h_good in hosts_find:
				if (h == h_good):
					y_n = True
			
			if not y_n:
				self.list_nofind.append(h)			# add nofind host in list
		logging.info( 'List no-find: ' + str(self.list_nofind) )
