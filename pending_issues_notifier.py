# -*- coding: utf-8 -*-
import mysqlconnection
import os
from mysqlconnection import cur
import subprocess
from ipdb import set_trace

HOST="root@10.231.202.242"
mymail = 'gabriel.leske@ree.es'
URL_BASE = 'http://10.231.202.242/dri/?q=node/'
COMMAND = ''

queries = [
	('SELECT * FROM `field_revision_field_psis_estado`', 'issues'),
	('SELECT * FROM `users`', 'users'),
	('SELECT * FROM `node`', 'nodes'),
	('SELECT * FROM `field_revision_field_psis_asignado`', 'assigned')
]

fetched_data = {}

for query in queries:
	cur.execute( query[0] )
	fetched_data[ query[1] ] = cur.fetchall()

solved = [issue for issue in fetched_data[ 'issues' ] if issue[7] == 37]
new_or_in_process = [issue for issue in fetched_data[ 'issues' ] if issue[7] == 35 or issue[7] == 36]


header = "Las siguientes incidencias del P-SIS creadas por ti se encuentran resueltas:\n"
footer = "\n\nPor favor verifica su resolución y procede a su cierre o reapertura.\nAnte cualquier duda ponte en contacto con Gabriel Leske: gabriel.leske@ree.es, Ext 3034."
mails_dict = {}

for issue in solved:
	nid = issue[3]
	node = [node for node in fetched_data[ 'nodes' ] if node[0] == nid][0]
	title = node[4]
	uid = node[5]
	link = URL_BASE + str(nid)
	user = [usuario for usuario in fetched_data[ 'users' ] if usuario[0] == uid][0]
	username = user[5]
	email = user[3]

	if email not in mails_dict:
		mails_dict[ email ] = 'Hola ' + username + ',\n\n' + header

	mails_dict[ email ] = mails_dict[ email ] + '\n' + title + ' ' + link

for mail in mails_dict:
	body = mails_dict[ mail ] + footer
	COMMAND = COMMAND + 'echo "' + body + '" | mail -s "ATENCION P-SIS" ' + mymail + ' -- -f portalDRI@ree.es\n'


header = "Tienes las siguientes incidencias del P-SIS asignadas:\n"
footer = "\n\nPor favor en caso de ser posible procede a su resolución.\nAnte cualquier duda ponte en contacto con Gabriel Leske: gabriel.leske@ree.es, Ext 3034."
mails_dict = {}

for issue in new_or_in_process:
	nid = issue[3]
	node = [node for node in fetched_data[ 'nodes' ] if node[0] == nid][0]
	title = node[4]
	uid = [node for node in fetched_data[ 'assigned' ] if node[3] == nid][0][7]
	link = URL_BASE + str(nid)
	user = [usuario for usuario in fetched_data[ 'users' ] if usuario[0] == uid][0]
	username = user[5]
	email = user[3]

	if email not in mails_dict:
		mails_dict[ email ] = 'Hola ' + username + ',\n\n' + header + email

	mails_dict[ email ] = mails_dict[ email ] + '\n' + title + ' ' + link

for mail in mails_dict:
	body = mails_dict[ mail ] + footer
	COMMAND = COMMAND + 'echo "' + body + '" | mail -s "ATENCION P-SIS" ' + mymail + ' -- -f portalDRI@ree.es\n'

ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ssh.stdout.readlines()