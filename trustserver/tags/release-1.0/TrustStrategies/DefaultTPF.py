from TrustPath import TrustPath	
from TrustPath import Fifo
from TrustPathFinder import TrustPathFinder


class DefaultTPF(TrustPathFinder):
	def query(self, source, sink, options):
		return str(options)

