from TrustPathFinder import TrustPathFinder

class PeopleListTPF(TrustPathFinder):
	def query(self, source, sink, options):
		return "|".join(self.people.keys())

