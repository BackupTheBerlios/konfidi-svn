from TrustPath import TrustPath	
from TrustPath import Fifo
from TrustPathFinder import TrustPathFinder
import xmlgen

class PeopleDumpTPF(TrustPathFinder):
	def query(self, source, sink, options):
		res = ""
		print "People: %d" % (len(self.people.items()))
		for (k, v) in self.people.items():
			res += "%s\n\n" % (v)
		
		f = xmlgen.Factory()
		trustresult = f.trustresult[f.rating("%d" % 0), f.data(res)]
		t = str(trustresult)
	
		return "%s" % t

