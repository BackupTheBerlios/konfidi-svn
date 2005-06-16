#!/usr/bin/env python
#  Copyright (C) 2005-2005 Dave Brondsema, Andrew Schamp
#  This file is part of Konfidi http://konfidi.org/
#  It is licensed under two alternative licenses (your choice):
#      1. Apache License, Version 2.0
#      2. GNU Lesser General Public License, Version 2.1
#
#
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import os
import time
import thread
import sys
import cfgparse

from select import select 

from UpdateListener import UpdateListener
from QueryListener import QueryListener
from RequestServer import RequestServer
from ReadWriteLock import ReadWriteLock

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
		self.lock = ReadWriteLock()
		self.updatePort = config.update_port
		self.queryPort = config.query_port
		# this people object should be the global object that is shared by both updateListener and queryListener
		self.people = people
		self.updateListener = RequestServer((self.host, self.updatePort), UpdateListener, self.people, self.lock, self.config)
		self.queryListener = RequestServer((self.host, self.queryPort), QueryListener, self.people, self.lock, self.config)
		
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
	c.add_option('trust_url', type='string', default='http://svn.berlios.de/viewcvs/*checkout*/konfidi/schema/trunk/trust.owl', keys='Schema')
	c.add_option('wot_url', type='string', default='http://xmlns.com/wot/0.1/', keys='Schema')
	c.add_option('rdf_url', type='string', default='http://www.w3.org/2000/01/rdf-schema', keys='Schema')
	c.add_option('strategy_password', type='string', default='konfidi', keys='Strategies')
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
	sys.exit(0)		

if __name__ == "__main__":
	# see if I'm already started
	# if so, just exit.
	try:
		os.mkdir(os.path.dirname(PIDFILE))
	except OSError:
		pass
	#pids = open(PIDFILE, 'r').read()
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
	try:
		os.mkdir(os.path.dirname(LOGFILE))
	except OSError:
		pass
	sys.stdout = sys.stderr = Log(open(LOGFILE, 'a+'))
	main()

