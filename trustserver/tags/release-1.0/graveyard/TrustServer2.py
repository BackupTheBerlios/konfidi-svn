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
import TrustValue

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
		self.request.send("Ok.")
		self.request.close()
		self.load(str)
		#self.load(openAnything(str))
		print "update connection closed."
	def load(self, source):	
		# TODO:  don't let duplicate trust levels on certain subjects be entered!	
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
			# we do this to make sure they exist.
			p2 = self.server.getPerson(f2)
			for value, resource in store.predicate_objects(trustee):
				if value in self.trustValues:
					p.addTrustLink(f2, resource.split("#")[1], resource, TrustValue.TrustValue(value.split("#")[1]))
			
class QueryListener(SocketServer.StreamRequestHandler):
	def handle(self):
		print "query connection!"
		str = ''
		data = self.request.recv(1024)
		try:
			[source,sink,subject] = data.split(":")
			self.request.send(self.server.query(source, sink, subject))
		except (ValueError):
			self.request.send("Invalid query")
		self.request.close()
		print "query connection closed."

class TrustServer(SocketServer.ThreadingTCPServer):
	"""This class allow everyone to have access to the 
	people lookup table"""
	def __init__(self, server_address, RequestHandlerClass, people={}):
		self.people = people
		SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)
		self.host = server_address[0]
		self.updatePort = server_address[1]+10
		self.queryPort = server_address[1]
		self.people = people
		self.updateListener = TrustServer((self.host, self.updatePort), UpdateListener, self.people)
		self.queryListener = TrustServer((self.host, self.queryPort), QueryListener, self.people)
		
	def startUpdateListener(self, junk):
		print "Starting Update Listener"
		self.updateListener.serve_forever()
		
	def startQueryListener(self, junk):
		print "Starting Update Listener"
		self.queryListener.serve_forever()
		
	def query(self, source, sink, subject="default"):
		return "search successful!: found %s, %s, %s." % (source, sink, subject)

if __name__ == "__main__":	
	print "Server Started"	
	t = TrustServer(('', 50000), SocketServer.StreamRequestHandler, {})
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
	