class TrustPathFinder:
	def __init__(self, source, sink, options):
		self.source = source
		self.sink = sink
		self.options = {}
		# split the list of options, and build a dictionary out of it
		for o in options.split("|"):
			(k, v) = o.split("=")
			self.options[k] = v
			
	def query(self, people):
		raise NotImplementedError