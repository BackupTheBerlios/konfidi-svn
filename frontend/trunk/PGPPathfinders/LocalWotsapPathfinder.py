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
		exec("from %s import wotsapmain" % (self.config["app"])
		out = StringIO()
		err = StringIO()
		oldout = sys.stdout
		olderr = sys.stderr
		
		sys.stdout = out
		sys.stdout = err
		
		wotsapmain(["-w", self.config["data"], source[-8:], sink[-8:])
		
		out = out.getvalue()
		err = err.getvalue()
		sys.stdout = oldout
		sys.stderr = olderr
		return (out, err)
