import sys
import os
import re

tc = "/usr/bin/python /home/ams5/public_html/trustserver/TrustClient.py"
files = [os.path.abspath(f) for f in os.listdir('.') if os.path.isfile(os.path.join('.', f)) and re.compile(".rdf$").search(f, 1)]
for f in files:
	os.system("%s localhost 20010 %s" % (tc, f))
