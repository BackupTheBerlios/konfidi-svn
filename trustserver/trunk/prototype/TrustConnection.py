class TrustConnection:
	"""contains a person and a list of trusted topics"""
	def __init__(self, fingerprint=None, trusts=None):
		self.fingerprint = fingerprint
		if (trusts == None): 
			self.trusts = []
		else:
			self.trusts = trusts
		
	def getFingerprint(self):
		return self.fingerprint
		
	def setFingerprint(self, fingerprint):
		self.fingerprint = fingerprint

	def addTrustSubject(self, trustSubject):
		self.trusts.append(trustSubject)
		
	def getTrusts(self):
		return self.trusts
		
	def setTrusts(self, trusts):
		self.trusts = trusts

	def __repr__(self):
		return "%s on: %s" % (self.fingerprint, self.trusts) 

		