#!/usr/bin/python
# -*- coding: utf-8

from pyzabbix import ZabbixAPI
import time
import MySQLdb
import os
#import sys
import re
import datetime
from Bruterbrod import Bruter



# FUNC - CREATE FILE FROM ZBX-API-HOSTS-LIST
# Создает файл host1.lst, содержащий id,host-ip
def ZBX_api_get_list():
	startTime = time.time()
	file_name = 'hosts1.lst'
	zapi = ZabbixAPI(server="https://zbxapi.idontknow.io")
	zapi.login("XXX", "XXX")
	i = 1
	f = open(file_name, 'w')
	for host in zapi.host.get(output="extend", filter={'snmp_available': 1}, groupids=[21]): 
		hid = host['hostid']
		hi = zapi.hostinterface.get(output="extend", filter={'hostid': hid})
		print "#"+str(i), hi[0]['hostid'], hi[0]['dns'], hi[0]['ip']
		line = hi[0]['hostid'] + ';' + hi[0]['dns']  + ';' + hi[0]['ip'] + ';;'
		f.write (line + '\n')
		i += 1
	
	f.close()
	print "[*] Create file hosts1.lst consist hosts ids (Spend: {:.3f} seconds)".format(time.time() - startTime)


# FUNC - CREATE FILE FROM MYSQLDB-HOSTS-LIST
# Создает файл host2.lst, содержит все типы хостов из бд забикса. Поля: id,Name, Название-шаблона
# Название шаблона необходимо, чтоб идентифицировать данное устройство как cisco,mikrotik,dlink или rwr
def MYSQL_get_list():
	startTime = time.time()
	print "[*] Connect to db: zabbix.xxx.io"
	# Get data from db mysql
	db = MySQLdb.connect(host="zabbix.xxx.io", user="xxxx", passwd="xxxx", db="XXX", charset='utf8')
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
	file_name = 'hosts2.lst'
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
	print "[*] Create file hosts2.lst consist hosts ids dns-name ip template-name (Spend: {:.3f} seconds)".format(time.time() - startTime)


# FUNC - READ LISTS FROM FILES AND COMBINE IN ONE
# Объеденяе данные из host1,host2 в файл host3.lst Данный файл имеет id, Name, ip-address, template-name
# Теперь известно, какой хост к какому типу устройств относится на основе шаблона
def Files_list_combine():
	hosts_list = []

	f = open('hosts1.lst', 'r')
	for line in f.readlines():
		arr_str = line.split(';')
		hosts_list.append(arr_str)
	f.close()

	f = open('hosts2.lst', 'r')
	for line in f.readlines():
		arr_str = line.split(';')
		hosts_list.append(arr_str)
	f.close()

	hosts_list.sort(key=lambda tup: tup[0])

	h_id = ''
	h_dns = ''
	h_ip = ''
	h_templ = ''
	h_id_old = ''

	host_arr = ['','','','']
	host_list_new = []

	i = 1
	n = 1
	for host in hosts_list:
		h_id = host[0]
		h_dns = host[1]
		h_ip = host[2]
		h_templ = host[3]
		
		if (h_id != h_id_old and n>1):
			#if (host_arr[1]!='' and host_arr[2]!='' and host_arr[3]!=''):
			host_list_new.append(host_arr)
			n = 1
			host_arr = ['','','','']
		
		host_arr[0] = h_id
		if (h_dns != ''):
			host_arr[1] = h_dns
		if (h_ip != ''):
			host_arr[2] = h_ip
		if (h_templ != ''):
			host_arr[3] = h_templ
		
		#print i, n, h_id, h_dns, h_ip, h_templ, '===>',host_arr

		i += 1
		n += 1
		h_id_old = h_id
	host_list_new.append(host_arr) # добавляем последние данные, которые при данном условии(if (h_id != h_id_old and n>1)) не добавляются
	return host_list_new


# FUNC - READ LISTS FROM FILES AND COMBINE IN ONE 2
# Объеденяе данные из host1,host2 в файл host4.lst Данный файл имеет id, Name, ip-address, template-name
# Теперь известно, какой хост к какому типу устройств относится на основе шаблона
def Files_list_combine2():
	hosts_list1 = []
	hosts_list2 = []
	one_host = []
	hosts_rez = []
	
	f = open('hosts1.lst', 'r')
	for line in f.readlines():
		arr_str = line.split(';')
		hosts_list1.append(arr_str)
	f.close()

	f = open('hosts2.lst', 'r')
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
	file_name = 'hosts3.lst'
	f = open(file_name, 'w')
	for host in hosts_rez:
		line = host[0] + ';' + host[1] + ';' + host[2] + ';' + host[3] + ';'
		f.write (line + '\n')
	f.close()


########################################################################
################### Create ip files ####################################
########################################################################

# FUNC - CREATE IP FILE FOR CISCO
def File_parse_cisco(file_name):
	hosts_cisco = []
	f = open(file_name, 'r')
	for line in f.readlines():
		if (re.search('cisco', line, re.IGNORECASE)):
			#print line,
			hosts_cisco.append(line)
	f.close()
	
	f = open('hosts_cisco.lst', "w")
	for host in hosts_cisco:
		f.write(host)
	f.close()
	
	f = open('ip_cisco.lst', 'w')
	for host in hosts_cisco:
		host_arr = host.split(';')
		f.write(host_arr[2]+"\n")
	f.close()


# FUNC - CREATE IP FILE FOR DLINK
def File_parse_dlink(file_name):
	hosts_dlink = []
	f = open(file_name, 'r')
	for line in f.readlines():
		if (re.search('link', line, re.IGNORECASE)):
			#print line,
			hosts_dlink.append(line)
	f.close()
	
	f = open('hosts_dlink.lst', "w")
	for host in hosts_dlink:
		f.write(host)
	f.close()
	
	f = open('ip_dlink.lst', 'w')
	for host in hosts_dlink:
		host_arr = host.split(';')
		f.write(host_arr[2]+"\n")
	f.close()


# FUNC - CREATE IP FILE FOR RWR
def File_parse_rwr(file_name):
	hosts_rwr = []
	f = open(file_name, 'r')
	for line in f.readlines():
		if (re.search('rwr', line, re.IGNORECASE)):
			#print line,
			hosts_rwr.append(line)
	f.close()
	
	f = open('hosts_rwr.lst', "w")
	for host in hosts_rwr:
		f.write(host)
	f.close()
	
	f = open('ip_rwr.lst', 'w')
	for host in hosts_rwr:
		host_arr = host.split(';')
		f.write(host_arr[2]+"\n")
	f.close()


# FUNC - CREATE IP FILE FOR MIKROTIK
def File_parse_mikrotik(file_name):
	hosts_mikrotik = []
	f = open(file_name, 'r')
	for line in f.readlines():
		if (re.search('mikr', line, re.IGNORECASE)):
			#print line,
			hosts_mikrotik.append(line)
	f.close()
	
	f = open('hosts_mikrotik.lst', "w")
	for host in hosts_mikrotik:
		f.write(host)
	f.close()
	
	f = open('ip_mikrotik.lst', 'w')
	for host in hosts_mikrotik:
		host_arr = host.split(';')
		f.write(host_arr[2]+"\n")
	f.close()


# FUNC - CREATE IP FILE FOR CISCO-catalyst
def File_parse_catalyst(file_name):
	hosts_cisco_catalyst = []
	f = open(file_name, 'r')
	for line in f.readlines():
		if (re.search('catalyst', line, re.IGNORECASE)):
			#print line,
			hosts_cisco_catalyst.append(line)
	f.close()
	
	f = open('hosts_cisco_catalyst.lst', "w")
	for host in hosts_cisco_catalyst:
		f.write(host)
	f.close()
	
	f = open('ip_cisco_catalyst.lst', 'w')
	for host in hosts_cisco_catalyst:
		host_arr = host.split(';')
		f.write(host_arr[2]+"\n")
	f.close()


########################################################################
################### Create db files ####################################
########################################################################


# FUNC - CREATE IP FILE FOR CISCO
#Создаем готовый db файл для категории устройств cisco
def Create_db_cisco(file_name):
	hosts_cisco = []
	f = open(file_name, 'r')
	for line in f.readlines():
		hosts_cisco.append(line)
	f.close()
	
	f = open('cisco.db', "w")
	for host in hosts_cisco:
		f.write(host[:-1] + ":cisco:up\n")
	f.close()

# FUNC - CREATE IP FILE FOR CISCO-catalyst
#Создаем готовый db файл для категории устройств cisco-catalyst
def Create_db_cisco_catalyst(file_name):
	hosts_cisco = []
	f = open(file_name, 'r')
	for line in f.readlines():
		hosts_cisco.append(line)
	f.close()
	
	f = open('cisco_catalyst.db', "w")
	for host in hosts_cisco:
		f.write(host[:-1] + ":cisco:up\n")
	f.close()

# FUNC - CREATE IP FILE FOR DLINK
#Создаем готовый db файл для категории устройств dlink
def Create_db_dlink(file_name):
	hosts = []
	f = open(file_name, 'r')
	for line in f.readlines():
		hosts.append(line)
	f.close()
	
	f = open('dlink.db', "w")
	for host in hosts:
		f.write(host[:-1] + ":dlink:up\n")
	f.close()


# FUNC - CREATE IP FILE FOR RWR
#Создаем готовый db файл для категории устройств rwr
def Create_db_rwr(file_name):
	hosts = []
	f = open(file_name, 'r')
	for line in f.readlines():
		hosts.append(line)
	f.close()
	
	f = open('rwr.db', "w")
	for host in hosts:
		f.write(host[:-1] + ":rwr:up\n")
	f.close()


# FUNC - CREATE IP FILE FOR MIKROTIK
#Создаем готовый db файл для категории устройств mikrotik
def Create_db_mikrotik_ssh(file_name):
	hosts = []
	f = open(file_name, 'r')
	for line in f.readlines():
		hosts.append(line)
	f.close()
	
	f = open('mikrotik.db', "w")
	for host in hosts:
		f.write(host[:-1] + ":mikrotikssh:up\n")
	f.close()



########################################################################
######################### BRUTE TO ACK #################################
########################################################################



########################################################################
############################# BEGIN ####################################
########################################################################



# MAIN PROCEDURE
def main():
	startTime = time.time()
	print "[*] START"
	now = datetime.datetime.now()
	path_dir = now.strftime("%Y%m%d_%H%M")
	
	if not os.path.exists(path_dir):
		os.mkdir(path_dir)
	
	# INITIALIZING
	paths = {
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
		'file_cloginrc_cisco' : 'results_cisco.cloginrc',
		'file_cloginrc_cisco_catalyst' : 'results_cisco_catalyst.cloginrc',
		'file_cloginrc_dlink' : 'results_dlink.cloginrc',
		'file_cloginrc_rwr' : 'results_rwr.cloginrc',
		'file_cloginrc_mikrotik' : 'results_mikrotik.cloginrc',
		'file_log_telnet_test' : 'log_telnet_probes.log',
		'file_log_telnet_cisco_enable' : 'log_telnet_probes_cisco_en.log',
	}
	
	
	# BRUTE PASSWORDS AND CREATE ACK LISTS
	print "\n[*] START BRUTE LOGIN & PASSWORDS TO HOSTS FOR CISCO"
	c = Bruter(paths['file_ip_cisco'], 'logins.lst', 'paswds.lst', 3, 5)
	c.PrintParamsInit()
	c.BruteAcks()
	time.sleep(3)
	print "\n[*] START BRUTE CISCO ENABLE"
	c.BruteAcksCiscoEnable()
	time.sleep(2)
	print "\n[*] SAVE RESULTS IN FILE: results_cisco.cloginrc"
	c.SaveBruteResults(paths['file_ack_cisco'])
	c.SaveBrute4Rancid(paths['file_cloginrc_cisco'])
	
	print "\n[*] START BRUTE LOGIN & PASSWORDS TO HOSTS FOR CISCO CATALYST"
	c = Bruter(paths['file_ip_cisco_catalyst'], 'logins.lst', 'paswds.lst', 3, 5)
	c.PrintParamsInit()
	c.BruteAcks()
	time.sleep(3)
	print "\n[*] START BRUTE CISCO ENABLE"
	c.BruteAcksCiscoEnable()
	time.sleep(2)
	print "\n[*] SAVE RESULTS IN FILE: results_cisco_catalyst.cloginrc"
	c.SaveBruteResults(paths['file_ack_cisco_catalyst'])
	c.SaveBrute4Rancid(paths['file_cloginrc_cisco_catalyst'])
	
	print "\n[*] START BRUTE LOGIN & PASSWORDS TO HOSTS FOR DLINK"
	c = Bruter(paths['file_ip_dlink'], 'logins.lst', 'paswds.lst', 3, 5)
	c.PrintParamsInit()
	c.BruteAcks()
	time.sleep(3)
	print "\n[*] START BRUTE CISCO ENABLE"
	c.BruteAcksCiscoEnable()
	time.sleep(2)
	print "\n[*] SAVE RESULTS IN FILE: results_dlink.cloginrc"
	c.SaveBruteResults(paths['file_ack_dlink'])
	c.SaveBrute4Rancid(paths['file_cloginrc_dlink'])
	
	print "\n[*] START BRUTE LOGIN & PASSWORDS TO HOSTS FOR RWR"
	c = Bruter(paths['file_ip_rwr'], 'logins.lst', 'paswds.lst', 3, 5)
	c.PrintParamsInit()
	c.BruteAcks()
	time.sleep(3)
	print "\n[*] START BRUTE CISCO ENABLE"
	c.BruteAcksCiscoEnable()
	time.sleep(2)
	print "\n[*] SAVE RESULTS IN FILE: results_rwr.cloginrc"
	c.SaveBruteResults(paths['file_ack_rwr'])
	c.SaveBrute4Rancid(paths['file_cloginrc_rwr'])
	
	
	print "\n[*] START BRUTE LOGIN & PASSWORDS TO HOSTS FOR MIKROTIK BY SSH"
	c = Bruter(paths['file_ip_mikrotik'], 'logins.lst', 'paswds.lst', 3, 5)
	c.PrintParamsInit()
	c.BruteAcksSsh()
	time.sleep(3)
	c.SaveBruteResults(paths['file_ack_mikrotik'])
	c.SaveBrute4Rancid(paths['file_cloginrc_mikrotik'])
	

# START
if __name__ == "__main__":
	main()
