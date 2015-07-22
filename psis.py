# -*- coding: utf-8 -*-
from ipdb import set_trace 
import MySQLdb as mdb
import subprocess

class Psis:
	receivers = 'gabriel.leske@ree.es'
	queries = [
		('issues', 'SELECT * FROM `field_revision_field_psis_estado`'),
		('users', 'SELECT * FROM `users`'),
		('nodes', 'SELECT * FROM `node`'),
		('assigned', 'SELECT * FROM `field_revision_field_psis_asignado`'),
		('responsible', 'SELECT * FROM `field_data_field_psis_responsable`')
	]
	fetched_data = {}
	HOST = "root@10.231.202.242"

	def __init__(self, user, password):
		self.con = mdb.connect('127.0.0.1',user,password,'dri')
		self.cur = self.con.cursor()
		self.fetch_data()

	def fetch_data(self):
		for query in self.queries:
			self.cur.execute( query[1] )
			self.fetched_data[ query[0] ] = self.cur.fetchall()
		
		dri_issues = [issue for issue in self.fetched_data['issues']\
						for responsible in self.fetched_data['responsible']\
						if responsible[3] == issue[3] and responsible[7] == 83]

		self.open_issues = [issue[3] for issue in dri_issues if issue[7] == 35 or issue[7] == 36]
		self.closed_issues = [issue[3] for issue in dri_issues if issue[7] == 34 or issue[7] == 37]
	

	def notify_open_issues(self):
		URL_BASE = 'http://10.231.202.242/dri/?q=node/'
		mails_dict = {}
		issue_counter = {}
		usernames = {}
		command = ''

		for issue in self.open_issues:
			node = [node for node in self.fetched_data['nodes'] if node[0] == issue][0]
			title = node[4]
			uid = [node for node in self.fetched_data['assigned'] if node[3] == issue][0][7]
			user = [usuario for usuario in self.fetched_data['users'] if usuario[0] == uid][0]
			link = URL_BASE + str(issue)
			email = user[3]

			if email not in mails_dict:
				mails_dict[email] = ''
				issue_counter[email] = 0
				usernames[email] = user[5]

			mails_dict[email] = mails_dict[email] + '\n' + title + ' ' + link
			issue_counter[email] += 1

		body = ''
		for mail in mails_dict:
			body = body + usernames[mail] + ' (' + str(issue_counter[mail]) + '):' + mails_dict[mail] + '\n\n'

		command = 'echo "' + body + '" | mail -s "RESUMEN INCIDENCIAS P-SIS" ' + self.receivers + ' -- -f portalDRI@ree.es\n'
		self.ssh_bash_command(command)

	def ssh_bash_command(self, command):
		ssh = subprocess.Popen(["ssh", "%s" % self.HOST, command], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		ssh.stdout.readlines()

	def test(self):
		nodes = [node for nid in self.closed_issues for node in self.fetched_data['nodes'] if node[0] == nid]
		set_trace()

	def average(self, elements):
	    total = 0
	    for element in elements:
	        total += element
		return total/len(elements)
