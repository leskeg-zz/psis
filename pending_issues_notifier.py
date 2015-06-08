# -*- coding: utf-8 -*-
import mysqlconnection
from mysqlconnection import cur
from ipdb import set_trace

cur.execute('SELECT * FROM `field_revision_field_psis_estado`')
incidencias = cur.fetchall()

resueltas = [incidencia for incidencia in incidencias if incidencia[7] == 37]
nuevas_o_en_curso = [incidencia for incidencia in incidencias if incidencia[7] == 35 or incidencia[7] == 36]


cur.execute('SELECT * FROM `users`')
usuarios = cur.fetchall()

cur.execute('SELECT * FROM `node`')
nodes = cur.fetchall()


URL_BASE = 'http://10.231.202.242/dri/?q=node/'

mails_dict = {}
for resuelta in resueltas:
	nid = resuelta[3]
	node = [node for node in nodes if node[0] == nid][0]
	uid = node[5]
	link = URL_BASE + str(nid)
	title = node[4]
	email = [usuario for usuario in usuarios if usuario[0] == uid][0][14]

	if email not in mails_dict:
		mails_dict[ email ] = []

	mails_dict[ email ].append(title+ ': ' + link)
	# print email + '\t' + link 
print mails_dict