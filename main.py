# -*- coding: utf-8 -*-
from ipdb import set_trace 
from psis import Psis
import sys

psis_obj = Psis(sys.argv[1],sys.argv[2])
psis_obj.average_resolving_time()
psis_obj.issues_by_user()
psis_obj.issues_history()