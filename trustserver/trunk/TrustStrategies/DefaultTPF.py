from TrustPath import TrustPath	
from TrustPath import Fifo
from TrustPathFinder import TrustPathFinder
import xmlgen

class DefaultTPF(TrustPathFinder):
	def query(self, source, sink, options):
		f = xmlgen.Factory()
		trustresult = f.trustresult[f.rating(str(-1)), f.error("You must specify a strategy to use.  This is the default.")]
		return str(trustresult)

