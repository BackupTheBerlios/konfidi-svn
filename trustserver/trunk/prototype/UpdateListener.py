from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.constants import TYPE
from rdflib.TripleStore import TripleStore
from rdflib.constants import DATATYPE
import SocketServer
from TrustValue import TrustValue
from BasicTrustValue import BasicTrustValue

class UpdateListener(SocketServer.BaseRequestHandler):
	def setup(self):
		# Create a namespace object for the Friend of a friend namespace.
		self.FOAF = Namespace("http://xmlns.com/foaf/0.1/")
		self.TRUST = Namespace("http://brondsema.gotdns.com/svn/dmail/foafserver/trunk/schema/trust.owl")
		self.WOT = Namespace("http://xmlns.com/wot/0.1/")
		self.RDF = Namespace("http://www.w3.org/2000/01/rdf-schema#")
		# load trust values into list for later
		trust = TripleStore()
		trust.load("http://brondsema.gotdns.com/svn/dmail/foafserver/trunk/schema/trust.owl")
		self.trustValues = []
		for s in trust.subjects(self.RDF["subPropertyOf"], self.TRUST["trustValue"]):
			self.trustValues.append(s)
	def handle(self):
		print "update connection opened."
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
		print "Update Listener: parsing input: %s" % source
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
					p.addTrustLink(f2, resource.split("#")[1], resource, BasicTrustValue(value.split("#")[1]))