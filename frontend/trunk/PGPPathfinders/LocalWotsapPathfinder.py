from PGPPathfinder import PGPPathfinder
import os
import locale
import imp
from StringIO import StringIO

class LocalWotsapPathfinder(PGPPathfinder):
	"""Uses wotsap from http://www.lysator.liu.se/~jc/wotsap/ and it's nightly-generated dump file"""
	def graph(self, source, sink, limit=None):
		(out, err) = self.runwotsap(source, sink, limit)
		return out # + err

	def connected(self, source, sink, limit=None):
		(out, err) = self.runwotsap(source, sink, limit)
		return out != None # and len(err) == 0

	def runwotsap(self, source, sink, limit=None):
		"""note how wotsap doesn't support a long fingerprint, so we just take the last 8 chars"""
		file = None
		mod = None
		try:
			#(file, pathname, description) = imp.find_module("Wot", self.config["path"])
			#mod = imp.load_module("Wot", file, self.config["file"], description)
			mod = imp.load_source("Wot", self.config["app"])
		finally:
			pass
		#	file.close()
		
		#raise ImportError
		#raise ImportError
		#exec("from %s import Wot" % (self.config["app"]))
		
		# see also wotsapmain
		wot = mod.Wot(self.config["data"])
		try:
			web = wot.findpaths(source[-8:], sink[-8:], None)
		except mod.wotError, err:
			#errmsg = unicode(err).encode(encoding, 'replace')
			return (None, err)
		if web is None:
			return (None, "Sorry, unable to find path.")
			
		if "getpreferredencoding" in dir(locale):
			encoding = locale.getpreferredencoding()
		else:
			locale.setlocale(locale.LC_CTYPE, "")
			encoding = locale.nl.langinfo(locale.CODESET)
			
		return (wot.creategraph(web, format='txt').encode(encoding, 'replace'), None)
