class Person:
	"""A person is the fundamental element of the web of trust."""
	def __init__(self, fingerprint):
		"""fingerprint is the PGP fingerprint for this person """
		self.fingerprint = fingerprint
		# trusts is a dictionary mapping fingerprints 
		# to a dictionary mapping subjects to trust values
		self.trusts = {}
		
	def getFingerprint(self):
		return self.fingerprint
		
	def setFingerprint(self, fingerprint):
		self.fingerprint = fingerprint
	
	def addTrustLink(self, sink, name, value):
		if sink in self.trusts:
			t = self.trusts[sink]
		else :
			t = {}
		t[name] = float(value)
		self.trusts[sink] = t
	
	def __repr__(self):
		str = "%s trusts: " % self.fingerprint
		for p in self.trusts:
			str += "\n\t%s regarding:" % p 
			for s in self.trusts[p]:
				str += "\n\t\t%s at level %s" % (s, self.trusts[p][s])
		return str
		
