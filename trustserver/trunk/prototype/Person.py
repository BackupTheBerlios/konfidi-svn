class Person:
	"""A person is the fundamental element of the web of trust."""
	def __init__(self, fingerprint):
		"""f is the PGP fingerprint for this person """
		self.fingerprint = fingerprint
		self.trusts = []
		
	def getFingerprint(self):
		return self.fingerprint
		
	def setFingerprint(self, fingerprint):
		self.fingerprint = fingerprint
		
	def addConnection(self, trustConn):
		"""tc is a trust connection object"""
		self.trusts.append(trustConn)
		
	def delConnection(self, fingerprint):
		"""removes a connection from a list"""
		for conn in self.trusts:
			if (conn.getFingerprint() == fingerprint):
				self.trusts.remove(conn)
		
	def __repr__(self):
		return "%s trusts: %s" % (self.fingerprint, self.trusts )
		
