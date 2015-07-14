# -*- coding: utf-8 -*-
'''HOWTO: python pending_issues_notifier.py userMySQL passwordmySQL'''
import mysqlconnection
import os
from mysqlconnection import cur
import subprocess
from ipdb import set_trace

def get_data(issues, fetched_data):
	receivers = 'egarcia@ree.es,gmesquida@ree.es,jmanresa@ree.es,vbermudez@ree.es,gbonis@ree.es,gabriel.leske@ree.es,angel.moya@ree.es'
	URL_BASE = 'http://10.231.202.242/dri/?q=node/'
	mails_dict = {}
	issue_counter = {}
	usernames = {}
	COMMAND = ''

	for issue in issues:
		nid = issue[3]
		node = [node for node in fetched_data[ 'nodes' ] if node[0] == nid][0]
		title = node[4]
		uid = [node for node in fetched_data[ 'assigned' ] if node[3] == nid][0][7]
		user = [usuario for usuario in fetched_data[ 'users' ] if usuario[0] == uid][0]
		link = URL_BASE + str(nid)
		email = user[3]

		if email not in mails_dict:
			mails_dict[ email ] = ''
			issue_counter[ email ] = 0
			usernames[ email ] = user[5]

		mails_dict[ email ] = mails_dict[ email ] + '\n' + title + ' ' + link
		issue_counter[ email ] += 1

	body = ''
	for mail in mails_dict:
		body = body + usernames[ mail ] + ' (' + str(issue_counter[ mail ]) + '):' + mails_dict[ mail ] + '\n\n'

	COMMAND = 'echo "' + body + '" | mail -s "RESUMEN INCIDENCIAS P-SIS" ' + receivers + ' -- -f portalDRI@ree.es\n'
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

new_or_in_process = [issue for issue in fetched_data[ 'issues' ] if issue[7] == 35 or issue[7] == 36]

COMMAND = get_data(new_or_in_process, fetched_data)

ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ssh.stdout.readlines()