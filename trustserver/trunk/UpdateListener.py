from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.constants import TYPE
from rdflib.TripleStore import TripleStore
from rdflib.constants import DATATYPE
import SocketServer
import operator
import time
from TrustValue import TrustValue
from BasicTrustValue import BasicTrustValue
#from pickle import dumps

#local
#from dump import dump

class UpdateListener(SocketServer.BaseRequestHandler):
	def setup(self):
		# Create a namespace object for the Friend of a friend namespace.
		# figure out trailing pound thing...
		#self.FOAF = Namespace(self.server.config.foaf_url + "#")
		#self.TRUST = Namespace(self.server.config.trust_url + "#")
		#self.WOT = Namespace(self.server.config.wot_url + "#")
		#self.RDF = Namespace(self.server.config.rdf_url + "#")
		
		self.FOAF = Namespace("http://xmlns.com/foaf/0.1/#")
		self.TRUST = Namespace("http://brondsema.gotdns.com/svn/dmail/schema/trunk/trust.owl#")
		self.WOT = Namespace("http://xmlns.com/wot/0.1/#")
		self.RDF = Namespace("http://www.w3.org/2000/01/rdf-schema#")

		# load trust values into list for later
		#trust = TripleStore()
		#trust.load(self.server.config.trust_url)
		
		#trust.load("http://brondsema.gotdns.com/svn/dmail/schema/trunk/trust.owl#")
		#self.trustValues = []
		#for s in trust.subjects(self.RDF["subPropertyOf"], self.TRUST["trustValue"]):
		#	self.trustValues.append(s)
			
	def handle(self):
		#print "update connection opened."
		#print "FOAF: %s" % (self.FOAF)
		#print "TRUST: %s" % (self.TRUST)
		#print "WOT: %s" % (self.WOT)
		#print "RDF: %s" % (self.RDF)
		str = ''
		while 1:
			data = self.request.recv(1024)
			if not data: break
			str += data
		self.request.send("Ok.")
		self.request.close()
		self.load(str)
		#self.load(openAnything(str))
		#print "update connection closed."
		
	def load(self, source):	
		print "Update Listener: parsing input: %s" % source
		# this is the main object we're concerned with
		trust = TripleStore()
		trust.load(source)	
		#self.server.lock.acquire_write()
		# new version
		
		for (relationship, truster) in trust.subject_objects(self.TRUST["truster"]):
			source = self.server.getPerson(trust.objects(truster, self.WOT["fingerprint"]).next())
			sink = self.server.getPerson(trust.objects(trust.objects(relationship, self.TRUST["trusted"]).next(), self.WOT["fingerprint"]).next())
			for item in trust.objects(relationship, self.TRUST["about"]):
				topic = trust.objects(item, self.TRUST["topic"]).next().split("#")[1]
				rating = trust.objects(item, self.TRUST["rating"]).next()
				source.addTrustLink(sink.getFingerprint(), topic, rating)
		#self.server.lock.release_write()
		
