# -*- coding: utf-8 -*-
'''HOWTO: python pending_issues_notifier.py userMySQL passwordmySQL'''
import mysqlconnection
import os
from mysqlconnection import cur
import subprocess
from ipdb import set_trace

def get_data(issues, case, fetched_data, header, footer):
	URL_BASE = 'http://10.231.202.242/dri/?q=node/'
	mymail = 'gabriel.leske@ree.es'
	mails_dict = {}
	COMMAND = ''

	for issue in issues:
		nid = issue[3]
		node = [node for node in fetched_data[ 'nodes' ] if node[0] == nid][0]
		title = node[4]

		if case == 'solved':
			uid = node[5]
			user = [usuario for usuario in fetched_data[ 'users' ] if usuario[0] == uid][0]
		elif case == 'new_or_in_process':
			uid = [node for node in fetched_data[ 'assigned' ] if node[3] == nid][0][7]
			user = [usuario for usuario in fetched_data[ 'users' ] if usuario[0] == uid][0]
		
		link = URL_BASE + str(nid)
		username = user[5]
		email = user[3]

		if email not in mails_dict:
			mails_dict[ email ] = 'Hola ' + username + ',\n\n' + header

		mails_dict[ email ] = mails_dict[ email ] + '\n' + title + ' ' + link

	print '\nSe enviarán ' + case + ' emails a:'
	for mail in mails_dict:
		body = mails_dict[ mail ] + footer
		print mail
		COMMAND = COMMAND + 'echo "' + body + '" | mail -s "RESUMEN INCIDENCIAS P-SIS" ' + mail + ' -- -f portalDRI@ree.es\n'

	return COMMAND

queries = [
	('SELECT * FROM `field_revision_field_psis_estado`', 'issues'),
	('SELECT * FROM `users`', 'users'),
	('SELECT * FROM `node`', 'nodes'),
	('SELECT * FROM `field_revision_field_psis_asignado`', 'assigned')
]

HOST="root@10.231.202.242"
fetched_data = {}

for query in queries:
	cur.execute( query[0] )
	fetched_data[ query[1] ] = cur.fetchall()

solved = [issue for issue in fetched_data[ 'issues' ] if issue[7] == 37]
new_or_in_process = [issue for issue in fetched_data[ 'issues' ] if issue[7] == 35 or issue[7] == 36]


header = "Las siguientes incidencias del P-SIS creadas por ti se encuentran resueltas:\n"
footer = "\n\nPor favor verifica su resolución y procede a su cierre o reapertura."
COMMAND = get_data(solved, 'solved', fetched_data, header, footer)

header = "Tienes las siguientes incidencias del P-SIS asignadas:\n"
footer = "\n\nPor favor a ser posible procede a su resolución."
COMMAND = COMMAND + get_data(new_or_in_process, 'new_or_in_process', fetched_data, header, footer)

ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ssh.stdout.readlines()