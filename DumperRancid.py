#!/usr/bin/python
# -*- coding: utf-8

import os
import datetime
import time
import json
import logging
from ZabbixWorker import ZabbixWorker
from Bruterbrod import Bruter
from CopyrRancid import Copypasta
from DevCheck import DevCheck
from CopyrRancid import Copypasta

logging.basicConfig(filename='dumper.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)

class Dumper:
	def __init__(self):
		copyr = Copypasta()
		logging.info( 'Init class Dumper' )
		
		os.chdir('/home/XXXXX/zabbix_hosts')
		own_path = os.path.dirname(os.path.abspath(__file__))
		# read paths
		# для каждого региона стандартный набор файлов
		# эти файлы потом раскидываются по директориям своего региона
		with open(own_path + '/config_paths.json', 'r') as f:
			data = json.load(f)
		self.paths = data
		logging.info( 'Read file: config_paths.json' )
		# read groups
		with open(own_path + '/groups.json', 'r') as f:
			data = json.load(f)
		self.groups = data
		logging.info( 'Read file: groups.json' )
	
	
	# DUMP DATA FROM ZABBIX
	def DumpZbx(self):
		#---------------------------------------------------------------
		def MoveData(path_dir):
			logging.info( 'Move dump files to regions dirs' )
			self.path_dir = path_dir
			if not os.path.exists(self.path_dir):
				os.mkdir(self.path_dir)
			
			for k, v in self.paths.items():
				if os.path.exists(v):
					stroka_log = "copy: %s ===> ./%s/%s" % (v, self.path_dir, v)
					logging.info( stroka_log)
					os.rename(v, self.path_dir + '/' + v)
		#---------------------------------------------------------------
		#print "\n START"
		for g in self.groups:
			#print g
			logging.info( 'Region:' + g )
			dumper = ZabbixWorker(self.groups[g])
			dumper.ZabbixFetch()
			dumper.CreateIpLists()
			dumper.CreateDbFiles()
			logging.info( 'Move data to rancid' )
			MoveData(g)	# сохраняем в диретории, соответствующей региону (g). Регион - ключ, а значение = это списко id зон в забиксе
	
	
	# SYNC RANCID WITH NEW DUMP
	def SyncRancid(self):
		logging.info( u' Sync dump with rancid db' )
		copyr = Copypasta()
		copyr.SyncFiles()
	
	
	# BRUTE 
	def BruteX(self):
		#---------------------------------------------------------------
		# чтение ip-шников из файла типа router.db
		def OpenDbFile2List(file_name):
			result_list = []
			try:
				list_tmp = open(file_name, "r").readlines() #self.list_hosts
				for l in list_tmp:
					pos = l.find(':')
					ip_addr = l[:pos]
					if (ip_addr.find('#') == -1):
						result_list.append(ip_addr) # add ip address
					#print l[:pos]
				return result_list
			except(IOError): 
				#logging.error( u"[-] Check your file hosts-list path: ", self.file_hosts )
				return None
		# get ip list from file
		def OpenFile2List(file_name):
			result_list = []
			if (os.path.exists(file_name)):
				f_list = open(file_name, "r").readlines()
				for l in f_list:
					result_list.append(l[:-1])
				return result_list
			else:
				return None
		# сохранить список в файл
		def AddList2File(file_name, list_save):
			f = open(file_name, 'a')
			for item in list_save:
				str2save = item[0] + ';' + item[1] + ';' + item[2] + ';' + item[3] + ';'
				f.write("%s\n" % str2save)
			f.close()
		# очистить файл
		def FileClear(file_name):
			file(file_name, 'w').close()
		# добавить подобранные учетки
		def AppendFile2File(f_in, f_out):
			list_buffer = []
			if not (os.path.exists(f_in)):
				open(f_in, "w").close()
			list_buffer = open(f_in, "r").readlines()
			#print "===================>>>>> ", f_out
			f = open(f_out, 'a')
			for l in list_buffer:
				f.write(l)
			f.close()
		#---------------------------------------------------------------
		#
		# START
		#file_hosts = 'test_ip.lst'
		file_logins = 'logins.lst'
		file_paswds = 'paswds.lst'
		
		
		FileClear('results_find.lst')
		FileClear('results_rancids.cloginrc')
		FileClear('results_nofind.lst')
		
		# проходим по всем файлам route.db в rancid и берем из них списки хостов
		copyr = Copypasta()
		for p in copyr.copy_paths:		# p - это локальный дамп из забикса (фалы db)
			region_dir = p[:p.rfind('/')+1]	#выделяем директорию для данной группы и будем скидывать в нее все данные
			#print region_dir
			
			list_hosts = OpenDbFile2List(p)
			logging.info( u'Size of list hosts: ' + str(len(list_hosts)))
			
			# SET FILES
			logging.info( u'File hosts ' + p)
			list_ips = list_hosts
			list_logins = OpenFile2List(file_logins)
			list_paswds = OpenFile2List(file_paswds)
			
			# BRUTE INIT
			brute = Bruter(list_ips, list_logins, list_paswds, 3, 3) # Кладем ip адреса, логины и пароли в процедуру инициализаии класса Bruter 3 - timeout 2-thread
			#brute.bl.Del_AcksCloginrc()
			
			# BRUTE TELNET
			brute.bl.max_count = len(brute.bl.list_combs_telnet)
			logging.info( u'Brute telnet combinations count ' + str(len(brute.bl.list_combs_telnet)) )
			logging.info( u'Start brute' )
			brute.BruteAcksTelnet()
			
			# BRUTE CISCO-ENABLE
			brute.bl.Set_Combs_Cisco()
			brute.bl.max_count = len(brute.bl.list_combs_cisco)
			logging.info( u'Brute telnet cisco enable combinations count ' + str(len(brute.bl.list_combs_cisco)) )
			logging.info( u'Start brute cisco-enable' )
			brute.BruteAcksTelnetCiscoEnable()
			brute.bl.Add_CiscoEnable2Acks() # добавить аккаунты cisco-enable в общий список telnet аккаунтов
			#brute.bl.Del_AcksCloginrc()
					
			
			# BRUTE SSH
			brute.bl.max_count = len(brute.bl.list_combs_ssh)
			logging.info( u'Brute ssh combinations count' + str(len(brute.bl.list_combs_ssh)) )
			logging.info( u'Start ssh brute' )
			brute.BruteAcksSsh()
			
			# WRITE RESULTS
			logging.info( u'Write resutlts to files' )
			AddList2File(copyr.Get_pRezFind(), brute.bl.list_telnet_acks)										# add to 'results_find.lst'
			AddList2File(copyr.Get_pRezFind(), brute.bl.list_ssh_acks)											# add to 'results_find.lst'
			brute.Save4Rancid(copyr.Get_pRezRancid(), brute.bl.list_telnet_acks)				# add to 'results_rancids.cloginrc'
			brute.Save4Rancid(copyr.Get_pRezRancid(), brute.bl.list_ssh_acks)					# add to 'results_rancids.cloginrc'
			
			logging.info( u'Create no-find list' )
			brute.bl.Find_NoFind()	# заполним список brute.bl.list_nofind хостами, учетки к которым подобрать не удалось
			logging.info( u'Save no-find list' )
			brute.AddNoFind(copyr.Get_pRezNoFind())				#'results_nofind.lst'
			
			os.rename(copyr.Get_pRezFind(), region_dir + copyr.Get_pRezFind())			# move results_find.lst /home/admin/zabbix_hosts/Discovered_hosts/results_find.lst
			os.rename(copyr.Get_pRezNoFind(), region_dir + copyr.Get_pRezNoFind())
			os.rename(copyr.Get_pRezRancid(), region_dir + copyr.Get_pRezRancid())		# results_rancids.cloginrc 
			
			# APPEN RANCID .cloginrc
			AppendFile2File(copyr.Get_pRezRancid(), copyr.Get_pRancidCloginrc())					#'results_nofind.lst'	'/home/admin/.cloginrc'

time_start = time.time()
logging.info('Start programm')


dumper = Dumper()
dumper.DumpZbx()	# download data from zabbix
dumper.SyncRancid() # copy dump-db to rancid router.db
dumper.BruteX()		# brute hosts by default accounts


time_spend = time.time() - time_start
time_spend_str = time.strftime("%H:%M:%S", time.gmtime(time_spend))
logging.info('End programm programm at ' + str(time_spend_str))
