# -*- coding: utf-8 -*-
from ipdb import set_trace 
import MySQLdb as mdb
import sys

con = mdb.connect('127.0.0.1',sys.argv[1],sys.argv[2],'dri')
cur = con.cursor()