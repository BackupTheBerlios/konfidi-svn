#system
import SocketServer
#import pickle
import string

#local
from dump import dump

class QueryListener(SocketServer.BaseRequestHandler):
	def setup(self):
		self.people = self.server.people
		
	def handle(self):
		print "query connection opened."
		str = ''
		data = self.request.recv(1024)
		if data == "people":
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
					exec("from Strategies.%sTPF import %sTPF" % (strategy, strategy))
					exec("tpf = %sTPF(\"%s\", \"%s\", \"%s\")" % (strategy, source, sink, options))
				except (ImportError):
					from Strategies.DefaultTPF import DefaultTPF
					tpf = DefaultTPF(source, sink, options)
					
				result = tpf.query(self.people)
				
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
