from PGPPathfinder import PGPPathfinder
import os
from StringIO import StringIO

class LocalWotsapPathfinder(PGPPathfinder):
	"""Uses wotsap from http://www.lysator.liu.se/~jc/wotsap/ and it's nightly-generated dump file"""
	def graph(self, source, sink, limit=None):
		(out, err) = self.runwotsap(source, sink, limit)
		return err + out

	def connected(self, source, sink, limit=None):
		(out, err) = self.runwotsap(source, sink, limit)
		return len(out) != 0 and len(err) == 0

	def runwotsap(self, source, sink, limit=None):
		"""note how wotsap doesn't support a long fingerprint, so we just take the last 8 chars"""
		exec("from %s import Wot" % (self.config["app"]))
		
		# see also wotsapmain
		wot = Wot(self.config["data"])
		try:
			web = wot.findpaths(source[-8:], sink[-8:], None)
		except wotError, err:
			#errmsg = unicode(err).encode(encoding, 'replace')
			return (None, err)
		if web is None:
			return (None, "Sorry, unable to find path.")

		return (wot.creategraph(web, format='txt').encode(encoding, 'replace'), None)
