#system
import SocketServer
#import pickle
import string

#local
#from dump import dump

class QueryListener(SocketServer.BaseRequestHandler):
	def setup(self):
		self.people = self.server.people
		
	def handle(self):
		print "query connection opened."
		str = ''
		data = self.request.recv(1024)
		if data == "people":
			# if you re-implement this, you really ought to make it thread-safe
			pass
			#print "people: \n"
			#for p in self.people:
			#	print "\t%s" % (t.people[p])
			#print "\tpeople:\n\t"
			#print dump(self.people)
			#print dump(self.server.people)
	
			#print string.join(self.people, "\n\t")
			#self.request.send(string.join(self.people, "\n"))
		else:
			try:
				[strategy,source,sink,options] = data.split(":")
				print "\texecuting query: %s, %s, %s, %s" % (strategy, source, sink, options)
				#TPF = __import__("Strategies.%sTPF" % strategy)
				#tpf = TPF.
				try:
					exec("from TrustStrategies.%sTPF import %sTPF" % (strategy, strategy))
					exec("tpf = %sTPF(self.people)" % (strategy))
				except (ImportError):
					from Strategies.DefaultTPF import DefaultTPF
					tpf = DefaultTPF(self.people)
				self.server.lock.acquire_read()	
				result = tpf.query(source, sink, options)
				self.server.lock.release_read()
				#s = self.query(source, sink, subject)
				# check to see if we need to make this smarter/bigger
				self.request.send(result)
				print "\tfinished: %s" % result
			except (ValueError):
				self.request.send("Invalid query")
	#		except (TypeError):
	#			self.request.send("Connection closed")
		self.request.close()
		print "query connection closed."
