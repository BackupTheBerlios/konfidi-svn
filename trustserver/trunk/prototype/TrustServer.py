import time
import SocketServer
import thread
import sys

from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.constants import TYPE
from rdflib.TripleStore import TripleStore
from rdflib.constants import DATATYPE
import Person
import TrustConnection
import TrustSubject
import TrustValue

def openAnything(source):
    if source == "-":
		import sys
		return sys.stdin	
    # try to open with urllib (if source is http, ftp, or file URL)
    import urllib                         
    try:                                  
        return urllib.urlopen(source)
    except (IOError, OSError):            
        pass                              
    # try to open with native open function (if source is pathname)
    try:                                  
        return open(source)
    except (IOError, OSError):            
        pass                              
    # treat source as string
    import StringIO                       
    return StringIO.StringIO(str(source))

class RequestServer(SocketServer.ThreadingTCPServer):
	"""This class allow everyone to have access to the 
	people lookup table"""
	def __init__(self, server_address, RequestHandlerClass, people=None):
		self.people = people
		SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)
	def getPerson(self, fingerprint):
		"""Get a person for a given fingerprint 
		if one exists, otherwise, create one."""
		if fingerprint in self.people:
			p = self.people[fingerprint]
		else:
			p = Person.Person(fingerprint)
			self.people[fingerprint] = p
		return p

class UpdateListener(SocketServer.BaseRequestHandler):
	def setup(self):
		# Create a namespace object for the Friend of a friend namespace.
		self.FOAF = Namespace("http://xmlns.com/foaf/0.1/")
		self.TRUST = Namespace("http://www.abundantplunder.com/trust/owl/trust.owl#")
		self.WOT = Namespace("http://xmlns.com/wot/0.1/")
		self.RDF = Namespace("http://www.w3.org/2000/01/rdf-schema#")
		# load trust values into list for later
		trust = TripleStore()
		trust.load("http://www.abundantplunder.com/trust/owl/trust.owl#")
		self.trustValues = []
		for s in trust.subjects(self.RDF["subPropertyOf"], self.TRUST["trustValue"]):
			self.trustValues.append(s)
	def handle(self):
		print "update connection!"
		str = ''
		while 1:
			data = self.request.recv(1024)
			if not data: break
			str += data
		self.request.close()
		self.load(str)
		#self.load(openAnything(str))
		print "update connection closed."
	def load(self, source):		
		print "Update Listener: parsing input"
		# this is the main object we're concerned with
		store = TripleStore()
		store.load(source)			
		# For each foaf:Person in the store print out its mbox property.
		truster = store.subjects(self.TRUST["trusts"]).next()
		f = store.objects(truster, self.WOT["fingerprint"]).next()
		p = self.server.getPerson(f)
		for trustee in store.objects(truster, self.TRUST["trusts"]):
			f2 = store.objects(trustee, self.WOT["fingerprint"]).next()
			p2 = self.server.getPerson(f2)
			for value, subject in store.predicate_objects(trustee):
				if value in self.trustValues:
					name = subject.split("#")[1]
					resource = subject
					value = value.split("#")[1]
					tc = TrustConnection.TrustConnection()
					tc.setFingerprint(f2)
					tv = TrustValue.TrustValue(value)
					ts = TrustSubject.TrustSubject(name, resource, tv)
					tc.addTrustSubject(ts)
					p.addConnection(tc)
			
class QueryListener(SocketServer.BaseRequestHandler):
	def handle(self):
		print "query connection!"
		while 1:
			data = self.request.recv(1024)
			if not data: break
			self.request.send("Que: %s\n" % (data))
		self.request.close()
		print "query connection closed."

class TrustServer:	
	def __init__(self, host='', updatePort=50010, queryPort=50000, people={}):
		self.host = host
		self.updatePort = updatePort
		self.queryPort = queryPort
		self.people = people
		self.updateListener = RequestServer((self.host, self.updatePort), UpdateListener, self.people)
		self.queryListener = RequestServer((self.host, self.queryPort), QueryListener, self.people)
		
	def startUpdateListener(self, junk):
		print "Starting Update Listener"
		self.updateListener.serve_forever()
		
	def startQueryListener(self, junk):
		print "Starting Update Listener"
		self.queryListener.serve_forever()

if __name__ == "__main__":	
	print "Server Started"	
	t = TrustServer('', 50010, 50000, {})
	thread.start_new(t.startUpdateListener, ('',) )
	thread.start_new(t.startQueryListener, ('',) )
	# this is really just for output prettiness
	time.sleep(3)
	print "Server running.  Enter commands below: "
	while 1:
		cmd = sys.stdin.readline()
		print cmd
		if cmd.rstrip() == "quit": sys.exit(0)
		if cmd.rstrip() == "people": 
			for p in t.people:
				print t.people[p]
	