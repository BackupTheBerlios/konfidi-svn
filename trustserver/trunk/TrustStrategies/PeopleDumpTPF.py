from TrustPath import TrustPath	
from TrustPath import Fifo
from TrustPathFinder import TrustPathFinder


class PeopleDumpTPF(TrustPathFinder):
	def query(self, source, sink, options):
		res = ""
		for (k, v) in self.people.items():
			res += "%s\n\n" % (v)
		return "\n\npeople: %s" % (res)

