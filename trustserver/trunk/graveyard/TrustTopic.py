class TrustTopic:
	"""contains a name and some indicator of the topic"""
	def __init__(self, name=None, resource=None):
		self.name = name
		self.resource = resource
		
	def getName(self):
		return self.name
		
	def setName(self, name):
		self.name = name
		
	def getResource(self):
		return self.resource
	
	def setResource(self, resource):
		self.resource = resource

	def __repr__(self):
		return "<%s, %s>" % (self.name, self.resource)