class TrustSubject:
	"""contains a subject and trust value"""
	def __init__(self, name=None, resource=None, value=None):
		self.name = name
		self.resource = resource
		self.value = value
		
	def getName(self):
		return self.name
		
	def setName(self, name):
		self.name = name
		
	def getResource(self):
		return self.resource
		
	def setResource(self, resource):
		self.resource = resource
		
	def getValue(self):
		return self.value
		
	def setValue(self, value):
		self.value = value
	
	def __repr__(self):
		return "%s at level %s" % (self.name, self.value)