#system
import SocketServer
#import pickle
import string
import time

#local
#from dump import dump
from TrustPath import PathNotFoundError

class QueryListener(SocketServer.BaseRequestHandler):
	def setup(self):
		self.people = self.server.people
		
	def handle(self):
		print "query connection opened."
		str = ''
		data = self.request.recv(1024)
		try:
			[strategy,source,sink,options] = data.split(":")
			print "\texecuting query: %s, %s, %s, %s" % (strategy, source, sink, options)
			
			try:
				exec("from TrustStrategies.%sTPF import %sTPF" % (strategy, strategy))
				exec("tpf = %sTPF(self.people)" % (strategy))
			except (ImportError):
				from Strategies.DefaultTPF import DefaultTPF
				tpf = DefaultTPF(self.people)
				
			lockwait = time.time()
			self.server.lock.acquire_read()	
			lockwait = time.time() - lockwait
			searchtime = time.time()
			r = tpf.query(source, sink, options)
			searchtime = time.time() - searchtime
			result = "Result: %s\nQuery Execution Time: %.6f\nLock acquisition wait: %.6f" % (r, searchtime, lockwait)
			self.server.lock.release_read()
			
			# check to see if we need to make this smarter/bigger
			self.request.send(result)
			#print "\tfinished: %s" % result
		except KeyError, k:
			self.request.send("Person %s not found in dataset.\n" % (k))
		except PathNotFoundError, p:
			self.request.send("No path found from source to sink:\n%s\n\n" % (p)) 
		except (ValueError):
			self.request.send("Invalid query")
	
		self.request.close()
		print "query connection closed."
