class TrustValue:
	"""represents the level of trust.  might just be an int."""
	def __init__(self, value=None):
		self.value = value
		
	def getValue(self):
		return self.value
		
	def setValue(self, value):
		self.value = value
		
	def __repr__(self):
		return "%i" % (self.value)