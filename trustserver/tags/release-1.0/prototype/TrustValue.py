class TrustValue:
	trustValues = { \
	"trustsCompletely":None, "trustsHighly":None, \
	"trustsAveragely":None, "trustsMinimally":None, \
	"trustsNeutrally":None, "distrustsMinimally":None, \
	"distrustsAveragely":None, "distrustsHighly":None, \
	"distrustsCompletely":None }
	
	"""represents the level of trust.  might just be an int."""
	def __init__(self, value=None):
		self.value = value
#		raise NotImplementedError
		
	def getNumericValue(self):
		raise NotImplementedError
		
	def getValue(self):
		return self.value
		
	def setValue(self, value):
		self.value = value
		
	def __repr__(self):
		return "%s" % (self.value)
	
	def aggregate(self):
		raise NotImplementedError
		
	def concatenate(self):
		raise NotImplementedError