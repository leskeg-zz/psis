# -*- coding: utf-8 -*-
from ipdb import set_trace 
import MySQLdb as mdb

con = mdb.connect('127.0.0.1','root','rootREE','dri')
# cnx = connector.MySQLConnection(user=sys.argv[1], password=sys.argv[2], host='10.231.202.242', database='dri')
cur = con.cursor()