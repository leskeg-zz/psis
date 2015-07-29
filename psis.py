# -*- coding: utf-8 -*-
from ipdb import set_trace
from datetime import datetime 
import MySQLdb as mdb
import subprocess

class Psis:
	receivers = 'gabriel.leske@ree.es'
	queries = [
		('status', 'SELECT * FROM `field_revision_field_psis_estado`'),
		('users', 'SELECT * FROM `users`'),
		('nodes', 'SELECT * FROM `node`'),
		('assigned', 'SELECT * FROM `field_revision_field_psis_asignado`'),
		('responsible', 'SELECT * FROM `field_data_field_psis_responsable`'),
		('solved_by', 'SELECT * FROM `field_revision_field_psis_resuelto_por`')
	]
	fetched_data = {}
	nodes = {}
	HOST = "root@10.231.202.242"
	
	issue_states = {
		"34": 'closed',
		"35": 'new',
		"36": 'processing',
		"37": 'solved'
	}

	def __init__(self, user, password):
		self.con = mdb.connect('127.0.0.1',user,password,'dri')
		self.cur = self.con.cursor()
		self.fetch_data()

	def fetch_data(self):
		for query in self.queries:
			self.cur.execute( query[1] )
			self.fetched_data[ query[0] ] = self.cur.fetchall()
		
		self.dri_issues = [issue for issue in self.fetched_data['status']\
						for responsible in self.fetched_data['responsible']\
						if responsible[3] == issue[3]  and responsible[7] == 83]

		self.nodes['open_issues'] = [issue[3] for issue in self.dri_issues if issue[7] == 35 or issue[7] == 36]
		self.nodes['closed_issues'] = [issue[3] for issue in self.dri_issues if issue[7] == 34 or issue[7] == 37]
	

	def notify_open_issues(self):
		URL_BASE = 'http://10.231.202.242/dri/?q=node/'
		mails_dict = {}
		issue_counter = {}
		usernames = {}
		command = ''

		for issue in self.nodes['open_issues']:
			node = [node for node in self.fetched_data['nodes'] if node[0] == issue][0]
			title = node[4]
			uid = [node for node in self.fetched_data['assigned'] if node[3] == issue][0][7]
			user = self.get_user(uid)
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

	def average_resolving_time(self):
		# self.closed_issues_by_user = {}
		closed_issues = []
		nodes = [node for nid in self.nodes['closed_issues'] for node in self.fetched_data['nodes'] if node[0] == nid]
		for issue in issues:
			deltatime = issue[8]-issue[7]
			from datetime import datetime
			closed_issues.append((datetime.fromtimestamp(issue[7]).strftime('%Y-%m-%d %H:%M:%S'),float(deltatime)/(60*60*24)))			
			# if deltatime < 60*60*24*90:
			# 	uid = [assignement for assignement in self.fetched_data['solved_by'] if assignement[3] == issue[0]][0][7]
			# 	username = self.filter_administrator( self.get_user(uid)[5] )
				
			# 	try:
			# 		self.closed_issues_by_user[username].append((issue[0], deltatime))
			# 	except:
			# 		self.closed_issues_by_user[username] = [(issue[0], deltatime)]
		for d in closed_issues:
			print(str(d[0]) + '\t' + str(d[1]).replace('.',','))
		# self.average_time_closed_issues_by_user = {}
		# for username in self.closed_issues_by_user:
		# 	issues_quantity = len(self.closed_issues_by_user[username])
		# 	average_time = float(sum(self.closed_issues_by_user[username])/issues_quantity)
		# 	self.average_time_closed_issues_by_user[username] = (average_time/(60*60*24), issues_quantity)

	def get_user(self,uid):
		return [user for user in self.fetched_data['users'] if user[0] == uid][0]

	def filter_administrator(self,username):
		if username in ['Luis Vicente Charlesworth','Jos\xc3\xa9Vicente Sala Gasc\xc3\xb3n','Gabriel Leske']:
			username = 'Administrador'
		return username


	def issues_by_user(self):
		self.issues_status_by_user = {}
		for issue in self.dri_issues:
			uid = [node for node in self.fetched_data['assigned'] if node[3] == issue[3]][0][7]
			state = [node for node in self.fetched_data['status'] if node[3] == issue[3]][0][7]
			username = self.filter_administrator( self.get_user(uid)[5] )

			if not username:
				uid = [assignement for assignement in self.fetched_data['solved_by'] if assignement[3] == issue[3]][0][7]
				username = self.filter_administrator( self.get_user(uid)[5] )

			if username not in self.issues_status_by_user:
				self.issues_status_by_user[username] = {
					'closed':0,
					'new':0,
					'processing':0,
					'solved':0
				}
				self.issues_status_by_user[username][ self.issue_states[str(state)] ] += 1
			else:
				self.issues_status_by_user[username][ self.issue_states[str(state)] ] += 1

		print "{}\t{:<10}\t{:<10}\t{:<10}\t{:<10}".format('','Cerrado','Resuelto','En curso','Nuevo')
		for k,v in self.issues_status_by_user.iteritems():
			if k is not 'Administrador':
				print "{}\t{:<10}\t{:<10}\t{:<10}\t{:<10}".format(k.split(' ')[0],v['closed'],v['solved'],v['processing'],v['new'])

		print "{}\t{:<10}\t{:<10}\t{:<10}\t{:<10}".format(
			'Administrador',
			self.issues_status_by_user['Administrador']['closed'],
			self.issues_status_by_user['Administrador']['solved'],
			self.issues_status_by_user['Administrador']['processing'],
			self.issues_status_by_user['Administrador']['new']
		)

	def issues_creation_dates(self):
		dates = [ '1/' + datetime.fromtimestamp(node[7]).strftime('%m/%Y') for nid in self.dri_issues \
					for node in self.fetched_data['nodes'] if node[0] == nid[3]]
		self.cacl_monthly(dates)

	def issues_solved_dates(self):
		dates = ['1/' + datetime.fromtimestamp(node[7]).strftime('%m/%Y') for nid in self.nodes['closed_issues'] \
				for node in self.fetched_data['nodes'] if node[0] == nid]
		self.cacl_monthly(dates)

	def cacl_monthly(self,dates):
		issues = {}
		for date in dates:
			if date not in issues:
				issues[date] = 1
			else:
				issues[date] += 1

		for date,value in issues.iteritems():
			print(date + '\t' + str(value))