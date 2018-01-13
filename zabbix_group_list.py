#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyzabbix import ZabbixAPI

zapi = ZabbixAPI(server="https://zbxapi.xxxx.io")
zapi.login("user", "XXXX")

i =1
hostgroups = zapi.hostgroup.get(output="extend")
for g in hostgroups:
	print g
	i += 1
