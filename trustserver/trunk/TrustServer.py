#!/usr/bin/env python

import os
import time
import thread
import sys
import cfgparse

from select import select 

from UpdateListener import UpdateListener
from QueryListener import QueryListener
from RequestServer import RequestServer

# configure these paths:
LOGFILE = sys.path[0] + '/log/trustserver.log'
PIDFILE = sys.path[0] + '/run/trustserver.pid'

class Log:
    """file like for writes with auto flush after each write
    to ensure that everything is logged, even during an
    unexpected exit."""
    def __init__(self, f):
        self.f = f
    def write(self, s):
        self.f.write(s)
        self.f.flush()

class TrustServer:
	def __init__(self, config=None, people=None):
		self.host = config.host
		self.config = config
		self.updatePort = config.update_port
		self.queryPort = config.query_port
		# this people object should be the global object that is shared by both updateListener and queryListener
		self.people = people
		self.updateListener = RequestServer((self.host, self.updatePort), UpdateListener, self.people, self.config)
		self.queryListener = RequestServer((self.host, self.queryPort), QueryListener, self.people, self.config)
		
	def startUpdateListener(self, junk):
		print "Starting Update Listener"
		self.updateListener.serve_forever()
		
	def startQueryListener(self, junk):
		print "Starting Query Listener"
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
	c.add_option('trust_url', type='string', default='http://brondsema.gotdns.com/svn/dmail/foafserver/trunk/schema/trust.owl', keys='Schema')
	c.add_option('wot_url', type='string', default='http://xmlns.com/wot/0.1/', keys='Schema')
	c.add_option('rdf_url', type='string', default='http://www.w3.org/2000/01/rdf-schema', keys='Schema')
	c.add_file(sys.path[0] + '/trustserver.cfg', None, 'ini')
	config = c.parse()

	print "Server Started"	
	t = TrustServer(config, {})
	thread.start_new(t.startUpdateListener, ('',) )
	thread.start_new(t.startQueryListener, ('',) )
	# I don't know a better way to keep this from exiting, except maybe to fork 
	# new processes of the above, and then exit.:
	while 1:
		time.sleep(240)
		#print "people: \n"
		#for p in t.getPeople():
		#	print "\t%s" % (t.people[p])
	# this is really just for output prettiness
	#time.sleep(3)
	#print "Server running.  Enter commands below: "
	#selectables = [sys.stdin]
	#while 1:
	#	(input, output, exc) = select([sys.stdin], [], [sys.stdin], 60)
	#	if input:
	#		cmd = sys.stdin.readline()
	#		if cmd.rstrip() == "quit": 
	#			break
	#		elif cmd.rstrip() == "people": 
	#			for p in t.getPeople():
	#				print t.people[p]
	#		elif cmd.rstrip() == "help":
	#			print "commands: \n\tpeople -- print the people dictionary\n\tquit -- exit the server."
			#else:
			#	print cmd
	#os.unlink('/tmp/trustpipe')
	sys.exit(0)		

if __name__ == "__main__":
	# see if I'm already started
	# if so, just exit.
	pids = open(PIDFILE, 'r').read()
	(stdin, stdout, stderr) = os.popen3("ps aux | grep `cat %s` | grep -v grep" % PIDFILE)
	stdin.close()
	stderr.close()
	str = stdout.read().rstrip()
	if (len(str) > 0):
		# I've already started
		print >> sys.stderr, "TrustServer already running.  Exiting."
		sys.exit(1)
	
	# do the UNIX double-fork magic, see Stevens' "Advanced
	# Programming in the UNIX Environment" for details (ISBN 0201563177)
	try:
		pid = os.fork()
		if pid > 0:
			# exit first parent
			sys.exit(0)
	except OSError, e:
		print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
		sys.exit(1)

	# decouple from parent environment
	os.chdir("/")   #don't prevent unmounting....
	os.setsid()
	os.umask(0)

	# do second fork
	try:
		pid = os.fork()
		if pid > 0:
			# exit from second parent, print eventual PID before
			#print "Daemon PID %d" % pid
			open(PIDFILE,'w').write("%d"%pid)
			sys.exit(0)
	except OSError, e:
		print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
		sys.exit(1)

	# start the daemon main loop
	sys.stdout = sys.stderr = Log(open(LOGFILE, 'a+'))
	main()

