import time
import thread
import sys

from UpdateListener import UpdateListener
from QueryListener import QueryListener
from RequestServer import RequestServer

class TrustServer:
	def __init__(self, host='', updatePort=50010, queryPort=50000, people=None):
		self.host = host
		self.updatePort = updatePort
		self.queryPort = queryPort
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

if __name__ == "__main__":	
	print "Server Started"	
	t = TrustServer('', 50010, 50000, {})
	thread.start_new(t.startUpdateListener, ('',) )
	thread.start_new(t.startQueryListener, ('',) )
	# this is really just for output prettiness
	time.sleep(3)
	print "Server running.  Enter commands below: "
	while 1:
		cmd = sys.stdin.readline()
		if cmd.rstrip() == "quit": sys.exit(0)
		elif cmd.rstrip() == "people": 
			for p in t.getPeople():
				print t.people[p]
		else:
			print "commands: \n\tpeople -- print the people dictionary\n\tquit -- exit the server."
		#else:
		#	print cmd
		
	