import sys
import os
import re

tc = "svn cat http://brondsema.gotdns.com/svn/dmail/clients/simple/TrustClient.py | /usr/bin/python - "
files = [os.path.abspath(f) for f in os.listdir('.') if os.path.isfile(os.path.join('.', f)) and re.compile(".rdf$").search(f, 1)]
for f in files:
	os.system("%s localhost 20010 %s" % (tc, f))
