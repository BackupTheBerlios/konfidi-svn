from TrustPathFinder import TrustPathFinder
import xmlgen

class PeopleListTPF(TrustPathFinder):
	def query(self, source, sink, options):
		f = xmlgen.Factory()
		trustresult = f.trustresult[f.data("|".join(self.people.keys()))]
		t = str(trustresult)
		return "%s" % t

