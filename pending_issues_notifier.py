# -*- coding: utf-8 -*-
import mysqlconnection
from mysqlconnection import cur
from ipdb import set_trace

fetched_data = {}

queries = [
	('SELECT * FROM `field_revision_field_psis_estado`', 'issues'),
	('SELECT * FROM `users`', 'users'),
	('SELECT * FROM `node`', 'nodes')
]

for query in queries:
	cur.execute( query[0] )
	fetched_data[ query[1] ] = cur.fetchall()

solved = [issue for issue in fetched_data[ 'issues' ] if issue[7] == 37]
new_or_in_process = [issue for issue in fetched_data[ 'issues' ] if issue[7] == 35 or issue[7] == 36]

URL_BASE = 'http://10.231.202.242/dri/?q=node/'

mails_dict = {}
message = "Las siguientes incidencias del PSIS están resuelas, por favor verifica su resolución y procede a su cierre o reapertura. \r\n"

for issue in solved:
	nid = issue[3]
	node = [node for node in fetched_data[ 'nodes' ] if node[0] == nid][0]
	title = node[4]
	uid = node[5]
	link = URL_BASE + str(nid)
	email = [usuario for usuario in fetched_data[ 'users' ] if usuario[0] == uid][0][14]

	if email not in mails_dict:
		mails_dict[ email ] = message

	mails_dict[ email ] = mails_dict[ email ] + '\r\n' + title + ': ' + link

footer = "\n\n\rAnte cualquier duda contacta con Gabriel Leske: gabriel.leske@ree.es, Ext 3034."

for mail in mails_dict:
	mails_dict[ mail ] = mails_dict[ mail ] + footer

print mails_dict[ mail ]