from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.constants import TYPE

# Import RDFLib's default TripleStore implementation.
from rdflib.TripleStore import TripleStore

# Create a namespace object for the Friend of a friend namespace.
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
TRUST = Namespace("http://www.abundantplunder.com/trust/owl/trust.owl")
WOT = Namespace("http://xmlns.com/wot/0.1/")

store = TripleStore()

from rdflib.constants import DATATYPE

store.load("example.rdf")

# Iterate over triples in store and print them out.
print "--- printing raw triples ---"
for s, p, o in store:
    print "S: %s\nP: %s\nO: %s\n" % (s, p, o)
    
# For each foaf:Person in the store print out its mbox property.
print "--- printing those who trust: ---"
truster = store.subjects(TRUST["trusts"]).next()
print truster

print "\n--- printing those who are trusted: ---"
for trusted in store.objects(truster, TRUST["trusts"]):
	print trusted
	#print "name: %s" % store.objects(trusted, FOAF["name"]).next()
	#print "fingerprint: %s" % store.objects(trusted, WOT["fingerprint"]).next()
	#print "trusted re:"
	#for subj in store.objects(trusted, TRUST["trustedCompletely"]):
	#	print TRUST["trustedCompletely"], subj
	#for subj in store.objects(trusted, TRUST["trustedHighly"]):
	#	print TRUST["trustedHighly"], subj
	#for subj in store.objects(trusted, TRUST["trustedAveragely"]):
	#	print TRUST["trustedAveragely"], subj
	#for subj in store.objects(trusted, TRUST["trustedMinimally"]):
	#	print TRUST["trustedMinimally"], subj
	#for subj in store.objects(trusted, TRUST["trustedNeutrally"]):
	#	print TRUST["trustedNeutrally"], subj
	#for subj in store.objects(trusted, TRUST["distrustedMinimally"]):
	#	print TRUST["distrustedMinimally"], subj
	#for subj in store.objects(trusted, TRUST["distrustedAveragely"]):
	#	print TRUST["distrustedAveragely"], subj
	#for subj in store.objects(trusted, TRUST["distrustedHighly"]):
	#	print TRUST["distrustedHighly"], subj
	#for subj in store.objects(trusted, TRUST["distrustedCompletely"]):
	#	print TRUST["distrustedCompletely"], subj
	print "---"