#system
import SocketServer
import string
import time
import imp
from xml.dom import minidom

#local
import xmlgen
from TrustPath import PathNotFoundError

class QueryListener(SocketServer.BaseRequestHandler):
	def setup(self):
		self.people = self.server.people
		
	def handle(self):
		data = self.request.recv(1024)
		try:
			[strategy,source,sink,options] = data.split(":")
			print "\texecuting query: %s, %s, %s, %s" % (strategy, source, sink, options)
			
			try:
				exec("from TrustStrategies.%sTPF import %sTPF" % (strategy, strategy))
				exec("tpf = %sTPF(self.people)" % (strategy))
				
			except (ImportError), i:
				from TrustStrategies.DefaultTPF import DefaultTPF
				tpf = DefaultTPF(self.people)
				print "%s" % (i)
			lockwait = time.time()
			self.server.lock.acquire_read()	
			lockwait = "%.6f" %  (time.time() - lockwait)
			searchtime = time.time()
			r = tpf.query(source, sink, options)
			searchtime = "%.6f" % (time.time() - searchtime)
			self.server.lock.release_read()
			
			# build the xml response
			f = xmlgen.Factory()
			result = f.queryresult(r, executed="1", strategy=strategy, search_time=searchtime, lock_time=lockwait)
			r = str(result)
			# check to see if we need to make this smarter/bigger
			self.request.send("%s" % r)
			
		except KeyError, k:
			self.request.send("Person %s not found in dataset.\n" % (k))
		except PathNotFoundError, p:
			self.request.send("No path found from source to sink:\n%s\n\n" % (p)) 
		#except (ValueError):
		#	self.request.send("Invalid query")
	
		self.request.close()
	
