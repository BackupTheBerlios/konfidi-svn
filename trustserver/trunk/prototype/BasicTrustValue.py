from TrustValue import TrustValue

class BasicTrustValue(TrustValue):
	trustValues = { \
	"trustedCompletely":1, "trustedHighly":.85, \
	"trustedAveragely":.7, "trustedMinimally":.6, \
	"trustedNeutrally":.5, "distrustedMinimally":.4, \
	"distrustedAveragely":.3, "distrustedHighly":.15, \
	"distrustedCompletely":0 }
	
	"""represents the level of trust.  might just be an int."""
	#def __init__(self, value=None):
	#	self.value = value
		
	def getNumericValue(self):
		return self.trustValues[self.value]
		
	#def getValue(self):
	#	return self.value
		
	#def setValue(self, value):
	#	self.value = value
		
	def __repr__(self):
		return "%s" % (self.value)
	
	def aggregate(self):
		pass
		
	def concatenate(self):
		pass
