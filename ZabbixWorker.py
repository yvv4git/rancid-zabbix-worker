#!/usr/bin/python
# -*- coding: utf-8

from pyzabbix import ZabbixAPI
import time
import MySQLdb
import os
#import sys
import re
import datetime
import json
import logging
from CopyrRancid import Copypasta
#from Bruterbrod import Bruter

logging.basicConfig(filename='dumper.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)

class ZabbixWorker:
	"""
	Класс, который занимается брут-форсом
	"""
	
	def __init__(self, groups):
		self.groups = groups
		self.cp = Copypasta()	# здесь храним пути
	
	
	# GET DUMP FROM ZABBIX (API & DB)
	def ZabbixFetch(self):
		logging.info( 'Group list ids: ' + str(self.groups) )
		# Создает файл host1.lst, содержащий id,host-ip
		def ZBX_api_get_list():
			startTime = time.time()
			file_name = self.cp.Get_pHost1()  #self.paths['file_host1']#'hosts1.lst'
			logging.info( 'File name: ' + file_name )
			zapi = ZabbixAPI(server="https://xxxxxxxx.ru")
			zapi.login(self.cp.Get_aZbxApiLogin(), self.cp.Get_aZbxApiPaswd())
			i = 1
			f = open(file_name, 'w')
			for host in zapi.host.get(output="extend", filter={'snmp_available': 1}, groupids=self.groups): #[21]
				hid = host['hostid']
				hi = zapi.hostinterface.get(output="extend", filter={'hostid': hid})
				logging.info( '# ' + str(i) + hi[0]['hostid'] + hi[0]['dns'] + hi[0]['ip'])
				line = hi[0]['hostid'] + ';' + hi[0]['dns']  + ';' + hi[0]['ip'] + ';;'
				f.write (line + '\n')
				i += 1
			f.close()
			#print "[*] Create file hosts1.lst consist hosts ids (Spend: {:.3f} seconds)".format(time.time() - startTime)
			logging.info( 'Create file host1.lst: ' + str(time.time() - startTime) )
			
		# Создает файл host2.lst, содержит все типы хостов из бд забикса. Поля: id,Name, Название-шаблона
		# Название шаблона необходимо, чтоб идентифицировать данное устройство как cisco,mikrotik,dlink или rwr
		def ZBX_MYSQL_get_list():
			startTime = time.time()
			logging.info( 'Connect ot db: xxxxx.ru')
			# Get data from db mysql
			db = MySQLdb.connect(host="xxxx.ru", user=self.cp.Get_aZbxMsqlLogin(), passwd=self.cp.Get_aZbxMsqlPaswd(), db=self.cp.Get_aZbxMsqlDb(), charset='utf8')		# self.uac['zbx_mysql_login']	self.uac['zbx_mysql_paswd']		self.uac['zbx_mysql_db']
			cursor = db.cursor()
			sql = """SELECT 
							hosts.hostid AS hID, 
							hosts.proxy_hostid AS hProxyID, 
							hosts.host AS hHost, 
							hosts.status AS hStatus, 
							hosts.available AS hAvailable, 
							hosts_templates.templateid AS tID, 
							h2.host AS tName
						FROM 
							hosts
						LEFT JOIN 
							hosts_templates
						ON 
							hosts.hostid = hosts_templates.hostid
						LEFT JOIN 
							hosts as h2
						ON 
							h2.hostid = hosts_templates.templateid
						WHERE 
							hosts.status=0;"""
			cursor.execute(sql)
			data = cursor.fetchall()
			db.close()
			# Save data to file
			file_name = self.cp.Get_pHost2() #self.paths['file_host2']
			f = open(file_name, 'w')
			for rec in data:
				#mail, name = rec
				#print rec
				#hosts_list.append(rec)
				hid = str(rec[0])
				dns = str(rec[2])
				template_name = str(rec[6])
				line = hid + ';' + dns + ';' + ';' + template_name + ';'
				#print line
				f.write (line + '\n')
			f.close()
			logging.info( 'Create files from db data: hosts2.lst' + str(time.time() - startTime))
			
		# Объеденяе данные из host1,host2 в файл host4.lst Данный файл имеет id, Name, ip-address, template-name
		# Теперь известно, какой хост к какому типу устройств относится на основе шаблона
		def Files_list_combine2():
			hosts_list1 = []
			hosts_list2 = []
			one_host = []
			hosts_rez = []
			
			f = open(self.cp.Get_pHost1(), 'r') #self.paths['file_host1']
			for line in f.readlines():
				arr_str = line.split(';')
				hosts_list1.append(arr_str)
			f.close()

			f = open(self.cp.Get_pHost2(), 'r') #self.paths['file_host2']
			for line in f.readlines():
				arr_str = line.split(';')
				hosts_list2.append(arr_str)
			f.close()
			
			for h in hosts_list1:
				one_host = ['','','','']
				for h2 in hosts_list2:
					if (h2[0] == h[0]):
						#print h[0], h2
						# id
						one_host[0] = h[0]
						# dns
						'''
						if (h[1]!='' or h[1] is not None):
							print h[1]
							one_host[1] = h[1]
						'''
						if (h2[1]!='' or h2[1] is not None):
							#print h2[1]
							one_host[1] = h2[1]
						# ip
						if (h[2]!='' or h[2] is not None):
							one_host[2] = h[2]
						elif (h2[2]!='' or h2[2] is not None):
							one_host[2] = h2[2]
						
						if (h2[3]!='' or h2[3] is not None):
							if (re.search('Template',h2[3], re.IGNORECASE)):
								one_host[3] = h2[3]
						
						#print one_host
						hosts_rez.append(one_host)
			
			#return hosts_rez
			file_name = self.cp.Get_pHost3() #self.paths['file_host3']
			f = open(file_name, 'w')
			for host in hosts_rez:
				line = host[0] + ';' + host[1] + ';' + host[2] + ';' + host[3] + ';'
				f.write (line + '\n')
			f.close()
			
		
		ZBX_api_get_list()
		ZBX_MYSQL_get_list()
		Files_list_combine2()
		os.system('cat ' + self.cp.Get_pHost3()  + ' | uniq > ' + self.cp.Get_pHost4())  # self.paths['file_host3']  self.paths['file_host4']
	
	# CREATE IP LISTS FROM ZABBIX DUMPS
	def CreateIpLists(self):
		# создаем файл ip для CISCO
		def File_parse_cisco(file_name):
			hosts_cisco = []
			f = open(file_name, 'r')
			for line in f.readlines():
				if (re.search('cisco', line, re.IGNORECASE)):
					#print line,
					hosts_cisco.append(line)
			f.close()
			f = open(self.cp.Get_pHostCisco(), "w")	#self.paths['file_host_cisco']
			for host in hosts_cisco:
				f.write(host)
			f.close()
			f = open(self.cp.Get_pIpCisco(), 'w')	#self.paths['file_ip_cisco']
			for host in hosts_cisco:
				host_arr = host.split(';')
				f.write(host_arr[2]+"\n")
			f.close()
		
		# создаем файл ip для DLINK
		def File_parse_dlink(file_name):
			hosts_dlink = []
			f = open(file_name, 'r')
			for line in f.readlines():
				if (re.search('link', line, re.IGNORECASE)):
					#print line,
					hosts_dlink.append(line)
			f.close()
			
			f = open(self.cp.Get_pHostDlink(), "w")	#self.paths['file_host_dlink']
			for host in hosts_dlink:
				f.write(host)
			f.close()
			
			f = open(self.cp.Get_pIpDlink(), 'w')	# self.paths['file_ip_dlink']
			for host in hosts_dlink:
				host_arr = host.split(';')
				f.write(host_arr[2]+"\n")
			f.close()
		
		# создаем файл ip для RWR
		def File_parse_rwr(file_name):
			hosts_rwr = []
			f = open(file_name, 'r')
			for line in f.readlines():
				if (re.search('rwr', line, re.IGNORECASE)):
					#print line,
					hosts_rwr.append(line)
			f.close()
			f = open(self.cp.Get_pHostRwr(), "w")		#self.paths['file_host_rwr']
			for host in hosts_rwr:
				f.write(host)
			f.close()
			f = open(self.cp.Get_pIpRwr(), 'w')	#self.paths['file_ip_rwr']
			for host in hosts_rwr:
				host_arr = host.split(';')
				f.write(host_arr[2]+"\n")
			f.close()
		
		# создаем файл ip для MIKROTIK
		def File_parse_mikrotik(file_name):
			hosts_mikrotik = []
			f = open(file_name, 'r')
			for line in f.readlines():
				if (re.search('mikr', line, re.IGNORECASE)):
					#print line,
					hosts_mikrotik.append(line)
			f.close()
			f = open(self.cp.Get_pHostMik(), "w")	# self.paths['file_host_mikrotik']
			for host in hosts_mikrotik:
				f.write(host)
			f.close()
			f = open(self.cp.Get_pIpMik(), 'w')	# self.paths['file_ip_mikrotik']
			for host in hosts_mikrotik:
				host_arr = host.split(';')
				f.write(host_arr[2]+"\n")
			f.close()
		
		# создаем файл ip для CISCO-catalyst
		def File_parse_catalyst(file_name):
			hosts_cisco_catalyst = []
			f = open(file_name, 'r')
			for line in f.readlines():
				if (re.search('catalyst', line, re.IGNORECASE)):
					#print line,
					hosts_cisco_catalyst.append(line)
			f.close()
			
			f = open(self.cp.Get_pHostCiscoCatalyst(), "w")	#self.paths['file_host_cisco_catalyst']
			for host in hosts_cisco_catalyst:
				f.write(host)
			f.close()
			f = open(self.cp.Get_pIpCiscoCatalyst(), 'w')	#self.paths['file_ip_cisco_catalyst']
			for host in hosts_cisco_catalyst:
				host_arr = host.split(';')
				f.write(host_arr[2]+"\n")
			f.close()
		
		# выполняем функции, парсим файл host4 и получуем соотсветствующие списки ip
		File_parse_cisco(self.cp.Get_pHost4()) # создаем файл с ip адресами: ip_cisco.lst		self.paths['file_host4']
		File_parse_catalyst(self.cp.Get_pHost4())												#self.paths['file_host4']
		File_parse_dlink(self.cp.Get_pHost4()) # создаем файл с ip адресами: ip_dlink.lst		self.paths['file_host4']
		File_parse_rwr(self.cp.Get_pHost4()) # создаем файл с ip адресами: ip_rwr.lst			self.paths['file_host4']
		File_parse_mikrotik(self.cp.Get_pHost4()) # создаем файл с ip адресами: ip_mikrotik.lst	self.paths['file_host4']
		
		
	# CREATE DB FILES
	def CreateDbFiles(self):
		#Создаем готовый db файл для категории устройств cisco
		def Create_db_cisco(file_name):
			hosts_cisco = []
			f = open(file_name, 'r')
			for line in f.readlines():
				hosts_cisco.append(line)
			f.close()
			f = open(self.cp.Get_pDbCisco(), "w")		#self.paths['file_db_cisco']
			for host in hosts_cisco:
				f.write(host[:-1] + ":cisco:up\n")
			f.close()
		#Создаем готовый db файл для категории устройств cisco-catalyst
		def Create_db_cisco_catalyst(file_name):
			hosts_cisco = []
			f = open(file_name, 'r')
			for line in f.readlines():
				hosts_cisco.append(line)
			f.close()
			f = open(self.cp.Get_pDbCiscoCatalyst(), "w")		#self.paths['file_db_cisco_catalyst']
			for host in hosts_cisco:
				f.write(host[:-1] + ":cisco:up\n")
			f.close()
		#Создаем готовый db файл для категории устройств dlink
		def Create_db_dlink(file_name):
			hosts = []
			f = open(file_name, 'r')
			for line in f.readlines():
				hosts.append(line)
			f.close()
			f = open(self.cp.Get_pDbDlink(), "w")		#self.paths['file_db_dlink']
			for host in hosts:
				f.write(host[:-1] + ":dlink:up\n")
			f.close()
		#Создаем готовый db файл для категории устройств rwr
		def Create_db_rwr(file_name):
			hosts = []
			f = open(file_name, 'r')
			for line in f.readlines():
				hosts.append(line)
			f.close()
			
			f = open(self.cp.Get_pDbRwr(), "w")		#self.paths['file_db_rwr']
			for host in hosts:
				f.write(host[:-1] + ":rwr:up\n")
			f.close()
		#Создаем готовый db файл для категории устройств mikrotik
		def Create_db_mikrotik_ssh(file_name):
			hosts = []
			f = open(file_name, 'r')
			for line in f.readlines():
				hosts.append(line)
			f.close()
			f = open(self.cp.Get_pDbMik(), "w")		# self.paths['file_db_mikrotik']
			for host in hosts:
				f.write(host[:-1] + ":mikrotikssh:up\n")
			f.close()
		#создаем db файлы 
		#print "[*] Create db files"
		Create_db_cisco(self.cp.Get_pIpCisco())		# self.paths['file_ip_cisco']
		Create_db_cisco_catalyst(self.cp.Get_pIpCiscoCatalyst())					# self.paths['file_ip_cisco_catalyst']
		Create_db_dlink(self.cp.Get_pIpDlink())											#self.paths['file_ip_dlink']
		Create_db_rwr(self.cp.Get_pIpRwr())													#self.paths['file_ip_rwr']
		Create_db_mikrotik_ssh(self.cp.Get_pIpMik())										# self.paths['file_ip_mikrotik']





