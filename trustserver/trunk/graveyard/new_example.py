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

# Create a namespace object for the Friend of a friend namespace.
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
TRUST = Namespace("http://www.abundantplunder.com/trust/owl/trust.owl#")
WOT = Namespace("http://xmlns.com/wot/0.1/")
RDF = Namespace("http://www.w3.org/2000/01/rdf-schema#")

# this is the main object we're concerned with
store = TripleStore()
store.load("example2.rdf")

# master dictionary containing all the people
# will a plain old dictionary suffice, or do I need a hashtable?
people = {}

# load trust values into list for later
trust = TripleStore()
trust.load("http://www.abundantplunder.com/trust/owl/trust.owl#")
trustValues = []
for s in trust.subjects(RDF["subPropertyOf"], TRUST["trustValue"]):
	trustValues.append(s)

# For each foaf:Person in the store print out its mbox property.
print "--- printing trust: ---"
truster = store.subjects(TRUST["trusts"]).next()
f = store.objects(truster, WOT["fingerprint"]).next()
p = Person.Person(f)
people[f] = p

for trustee in store.objects(truster, TRUST["trusts"]):
	f2 = store.objects(trustee, WOT["fingerprint"]).next()
	p2 = Person.Person(f2)
	people[f2] = p2
	for value, subject in store.predicate_objects(trustee):
		if value in trustValues:
			name = subject.split("#")[1]
			resource = subject
			value = value.split("#")[1]
			tc = TrustConnection.TrustConnection()
			tc.setFingerprint(f2)
			tv = TrustValue.TrustValue(value)
			ts = TrustSubject.TrustSubject(name, resource, tv)
			tc.addTrustSubject(ts)
			p.addConnection(tc)

for p in people:
	print people[p]