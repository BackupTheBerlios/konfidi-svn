from TrustPath import TrustPath	
from TrustPath import Fifo
from TrustPathFinder import TrustPathFinder

class PrototypeTPF(TrustPathFinder):
	def query(self, source, sink, opts):
                options = {}
                # split the list of options, and build a dictionary out of it
                for o in opts.split("|"):
                        (k, v) = o.split("=")
                        options[k] = v
		path = self.findPath(source, sink, options["subject"])
		#print "final path to sink: %s" % path
		rating = self.getPathRating(path, options["subject"])
		#print "final rating: %s" % rating
		return "%s" % rating
	
	def findPath(self, source, sink, subject):
		#print "searching for: %s to %s regarding %s" % (source, sink, subject)
		paths = {}
		seen = {source:1}
		newpaths = { source:list([u"%s" % source]) }
		while sink not in seen:
			# keep only the longest paths.
			paths = newpaths
			newpaths = {}
			for p in paths:
				# save the current path
				curpath = paths[p]
				# for each child of p
				for s in self.people[p].trusts:
					if s not in seen:
						if (subject in self.people[p].trusts[s]) or ("default" in self.people[p].trusts[s]):
							# mark child as seen
							seen[s] = 1
							# add new path ending in child to path dict
							t = list(curpath)
							t.append(s)
							newpaths[s] = t
		paths = newpaths
		return paths[sink]
	
	def getRating(self, source, sink, subject):
		"""This function assumes that there is in fact a 
		connection between the source and the sink.  This
		ought to be established, though, in the findPath stage."""
		#print "getRating: %s -> %s" % (source, sink)
		if subject in self.people[source].trusts[sink]:
			rating = self.people[source].trusts[sink][subject].getNumericValue()
		else: 
			rating = self.people[source].trusts[sink]["default"].getNumericValue()
		#print "\trating: %s" % rating
		return rating
	
	def getPathRating(self, path, subject):
		source = path.pop(0)
		rating = 1
		while (len(path) > 0):
			sink = path.pop(0)
			rating = .5-(.5-rating)*self.getRating(source, sink, subject)
			source = sink
		#print "total rating: %s" % rating
		return rating