import sys
import os

files = ["laing.rdf", "brondsema.rdf", "schamp.rdf"]
for f in files:
	os.system("TrustClient.py localhost 50010 %s" % f)