import os
import time
import thread
import sys
import cfgparse

from select import select 

from UpdateListener import UpdateListener
from QueryListener import QueryListener
from RequestServer import RequestServer

class TrustServer:
	def __init__(self, config=None, people=None):
		self.host = config.host
		self.config = config
		self.updatePort = config.update_port
		self.queryPort = config.query_port
		self.people = people
		self.updateListener = RequestServer((self.host, self.updatePort), UpdateListener, self.people)
		self.queryListener = RequestServer((self.host, self.queryPort), QueryListener, self.people)
		
	def startUpdateListener(self, junk):
		print "Starting Update Listener"
		self.updateListener.serve_forever()
		
	def startQueryListener(self, junk):
		print "Starting Update Listener"
		self.queryListener.serve_forever()
		
	def getPeople(self):
		return self.people

def main():
	# load the configuration data
	c = cfgparse.ConfigParser()
	# default values
	c.add_option('host', type='string', default='localhost', keys='Server')
	c.add_option('update_port', type='int', default='50010', keys='Server')
	c.add_option('query_port', type='int', default='50000', keys='Server')
	c.add_option('foaf_url', type='string', default='http://xmlns.com/foaf/0.1/', keys='Schema')
	c.add_option('trust_url', type='string', default='http://www.abundantplunder.com/trust/owl/trust.owl#', keys='Schema')
	c.add_option('woturl', type='string', default='http://xmlns.com/wot/0.1/', keys='Schema')
	c.add_option('rdf_url', type='string', default='http://www.w3.org/2000/01/rdf-schema#', keys='Schema')
	c.add_file(sys.path[0] + '/trustserver.cfg', None, 'ini')
	config = c.parse()

	#os.mkfifo('/tmp/trustpipe')
	#fin = open('/tmp/trustpipe', 'r')
	
	print "Server Started"	
	t = TrustServer(config, {})
	thread.start_new(t.startUpdateListener, ('',) )
	thread.start_new(t.startQueryListener, ('',) )
	# this is really just for output prettiness
	time.sleep(3)
	print "Server running.  Enter commands below: "
	selectables = [sys.stdin]
	while 1:
		(input, output, exc) = select([sys.stdin], [], [sys.stdin], 60)
		if input:
			cmd = sys.stdin.readline()
			if cmd.rstrip() == "quit": 
				break
			elif cmd.rstrip() == "people": 
				for p in t.getPeople():
					print t.people[p]
			elif cmd.rstrip() == "help":
				print "commands: \n\tpeople -- print the people dictionary\n\tquit -- exit the server."
			#else:
			#	print cmd
	#os.unlink('/tmp/trustpipe')
	sys.exit(0)		

if __name__ == "__main__":	
	main()

