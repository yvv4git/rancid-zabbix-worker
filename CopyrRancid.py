#!/usr/bin/python
# -*- coding: utf-8

import os
import time
#import ntpath
import logging
from collections import OrderedDict

logging.basicConfig(filename='dumper.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)

class Copypasta:
	def __init__(self):
		self.copy_paths = {
		# XXX
		'/home/admin/zabbix_hosts/XXXX/cisco.db' : '/var/lib/rancid/XXX_cisco/router.db',
		'/home/admin/zabbix_hosts/XXXX/cisco_catalyst.db' : '/var/lib/rancid/XXX_cisco/router.db',
		'/home/admin/zabbix_hosts/XXXX/dlink.db' : '/var/lib/rancid/XXX_dlink/router.db',
		}
		self.list_rancid = []
		self.list_dump = []
		
		self.paths = {
			'file_host1' : 'hosts1.lst',
			'file_host2' : 'hosts2.lst',
			'file_host3' : 'hosts3.lst',
			'file_host4' : 'hosts4.lst',
			'file_host_cisco' : 'hosts_cisco.lst',
			'file_host_cisco_catalyst' : 'hosts_cisco_catalyst.lst',
			'file_host_dlink' : 'hosts_dlink.lst',
			'file_host_rwr' : 'hosts_rwr.lst',
			'file_host_mikrotik' : 'hosts_mikrotik.lst',
			'file_ip_cisco' : 'ip_cisco.lst',
			'file_ip_cisco_catalyst' : 'ip_cisco_catalyst.lst',
			'file_ip_dlink' : 'ip_dlink.lst',
			'file_ip_rwr' : 'ip_rwr.lst',
			'file_ip_mikrotik' : 'ip_mikrotik.lst',
			'file_db_cisco' : 'cisco.db',
			'file_db_cisco_catalyst' : 'cisco_catalyst.db',
			'file_db_dlink' : 'dlink.db',
			'file_db_rwr' : 'rwr.db',
			'file_db_mikrotik' : 'mikrotik.db',
			'file_brute_raw_cisco' : 'brute_cisco_telnet.raw',
			'file_brute_raw_cisco_catalyst' : 'brute_cisco_catalyst_telnet.raw',
			'file_brute_raw_dlink' : 'brute_dlink_telnet.raw',
			'file_brute_raw_rwr' : 'brute_rwr_telnet.raw',
			'file_brute_raw_mikrotik' : 'brute_rwr_ssh.raw',
			'file_ack_cisco' : 'ack_cisco',
			'file_ack_cisco_catalyst' : 'ack_cisco_catalyst',
			'file_ack_dlink' : 'ack_dlink',
			'file_ack_rwr' : 'ack_rwr',
			'file_ack_mikrotik' : 'ack_mikrotik',
			'file_rez_find' : 'results_find.lst',
			'file_rez_nofind' : 'results_nofind.lst',
			'file_rez_rancid' : 'results_rancids.cloginrc',
			#'file_cloginrc_cisco' : 'results_cisco.cloginrc',
			#'file_cloginrc_cisco_catalyst' : 'results_cisco_catalyst.cloginrc',
			#'file_cloginrc_dlink' : 'results_dlink.cloginrc',
			#'file_cloginrc_rwr' : 'results_rwr.cloginrc',
			#'file_cloginrc_mikrotik' : 'results_mikrotik.cloginrc',
			#'file_log_telnet_test' : 'log_telnet_probes.log',
			#'file_log_telnet_cisco_enable' : 'log_telnet_probes_cisco_en.log',
			'file_rancid_acks' : '/home/admin/.cloginrc',
		}
		
		self.uac = {
			'zbxapi_login' : 'XXXX',
			'zbxapi_paswd' : 'XXXX',
			'zbx_mysql_login' : 'XXXX',
			'zbx_mysql_paswd' : 'XXXX',
			'zbx_mysql_db' : 'XXXX',
		}
	
	#-------------------------------------------------------------------
	def Get_pHost1(self):
		return self.paths['file_host1']
	def Get_pHost2(self):
		return self.paths['file_host2']
	def Get_pHost3(self):
		return self.paths['file_host3']
	def Get_pHost4(self):
		return self.paths['file_host4']
	# hosts
	def Get_pHostCisco(self):
		return self.paths['file_host_cisco']
	def Get_pHostCiscoCatalyst(self):
		return self.paths['file_host_cisco_catalyst']
	def Get_pHostDlink(self):
		return self.paths['file_host_dlink']
	def Get_pHostRwr(self):
		return self.paths['file_host_rwr']
	def Get_pHostMik(self):
		return self.paths['file_host_mikrotik']
	# ip
	def Get_pIpCisco(self):
		return self.paths['file_ip_cisco']
	def Get_pIpCiscoCatalyst(self):
		return self.paths['file_ip_cisco_catalyst']
	def Get_pIpDlink(self):
		return self.paths['file_ip_dlink']
	def Get_pIpRwr(self):
		return self.paths['file_ip_rwr']
	def Get_pIpMik(self):
		return self.paths['file_ip_mikrotik']
	# db
	def Get_pDbCisco(self):
		return self.paths['file_db_cisco']
	def Get_pDbCiscoCatalyst(self):
		return self.paths['file_db_cisco_catalyst']
	def Get_pDbDlink(self):
		return self.paths['file_db_dlink']
	def Get_pDbRwr(self):
		return self.paths['file_db_rwr']
	def Get_pDbMik(self):
		return self.paths['file_db_mikrotik']
	# brute - raw
	def Get_pBrCisco(self):
		return self.paths['file_brute_raw_cisco']
	def Get_pBrCiscoCatalyst(self):
		return self.paths['file_brute_raw_cisco_catalyst']
	def Get_pBrDlink(self):
		return self.paths['file_brute_raw_dlink']
	def Get_pBrRwr(self):
		return self.paths['file_brute_raw_rwr']
	def Get_pBrMik(self):
		return self.paths['file_brute_raw_mikrotik']
	# results
	def Get_pRezRancid(self):
		return self.paths['file_rez_rancid']
	def Get_pRezFind(self):
		return self.paths['file_rez_find']
	def Get_pRezNoFind(self):
		return self.paths['file_rez_nofind']

	# rancid .cloginrc
	def Get_pRancidCloginrc(self):
		return self.paths['file_rancid_acks']
	
	# accounts
	def Get_aZbxApiLogin(self):
		return self.uac['zbxapi_login']
	def Get_aZbxApiPaswd(self):
		return self.uac['zbxapi_paswd']
	def Get_aZbxMsqlLogin(self):
		return self.uac['zbx_mysql_login']
	def Get_aZbxMsqlPaswd(self):
		return self.uac['zbx_mysql_paswd']
	def Get_aZbxMsqlDb(self):
		return self.uac['zbx_mysql_db']
	
	def PrintPaths(self):
		for d in self.copy_paths:
			print d, '<===>',self.copy_paths[d]
	
	
	def SyncFiles(self):
		
		def merge_lists(lst1, lst2):
			for i in lst2:
				if i not in lst1:
					lst1.append(i)
			return lst1
		
		for d in self.copy_paths:
			if (os.path.exists(d) and os.path.exists(self.copy_paths[d])):
				self.list_rancid = open(d, "r").readlines()
				self.list_dump = open(self.copy_paths[d], "r").readlines()
			
				list_new = merge_lists(self.list_rancid, self.list_dump)
				list_new = list(set(list_new))  # delete dublicates
			
				logging.info( 'Rewrite file: ' + self.copy_paths[d] )
				fo = open(self.copy_paths[d], "w")
				fo.writelines(list_new)
				fo.close()
			else:
				logging.info( 'File not found: ' + self.copy_paths[d] + ' OR ' + d)
				pass
			
			time.sleep(0.3)

