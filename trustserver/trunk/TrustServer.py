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
import ConfigParser
        
from log4py import Logger, LOGLEVEL_DEBUG

#from select import select 

from UpdateListener import UpdateListener
from QueryListener import QueryListener
from RequestServer import RequestServer
from ReadWriteLock import ReadWriteLock

# configure these paths:
#LOGFILE = sys.path[0] + '/log/trustserver.log'
PIDFILE = sys.path[0] + '/run/trustserver.pid'

#class Log:
#    """file like for writes with auto flush after each write
#    to ensure that everything is logged, even during an
#    unexpected exit."""
#    def __init__(self, f):
#        self.f = f
#    def write(self, s):
#        self.f.write(s)
#        self.f.flush()

class TrustServer:
    def __init__(self, config=None, people=None):
        self.config = config
        self.lock = ReadWriteLock()
        # this people object should be the global object that is shared by both updateListener and queryListener
        self.people = people
        self.updateListener = RequestServer((self.config.get('Server', 'host'), int(self.config.get('Server', 'update_port'))), UpdateListener, self.people, self.lock, self.config)
        self.queryListener = RequestServer((self.config.get('Server', 'host'), int(self.config.get('Server', 'query_port'))), QueryListener, self.people, self.lock, self.config)
    
        # logging
        self.log = Logger().get_instance(self)
        self.log.info("Creating TrustServer")
    
    def startUpdateListener(self, foo=None):
        self.log.info("Starting Update Listener on port %s" % self.config.get('Server', 'update_port'))
        self.updateListener.serve_forever()
    
    def startQueryListener(self, foo=None):
        self.log.info("Starting Query Listener on port %s" % self.config.get('Server', 'query_port'))
        self.queryListener.serve_forever()
    
    def getPeople(self):
        return self.people

def check_defaults(config):
    """This function takes a config file and fills in default values, specified
    in the dictionary 'config_defaults', with a dictionary for each section 
    keyed by section name, below.  It returns the updated config object."""
    config_defaults = { 
        'Server'    : { 'host'         : 'localhost',
                        'update_port'  : '50010',
                        'query_port'   : '50000' },
        'Schema'    : { 'foaf_url'     : 'http://xmlns.com/foaf/0.1/',
                        'trust_url'    : 'http://svn.berlios.de/viewcvs/*checkout*/konfidi/schema/trunk/trust.owl',
                        'wot_url'      : 'http://xmlns.com/wot/0.1/',
                        'rdf_url'      : 'http://www.w3.org/2000/01/rdf-schema' },
        'Strategies' : {'strategy_password' : 'konfdi' }
    }
    for (section, entry) in config_defaults.items():
        for (k, v) in entry.items():
            if config.has_section(section):
                try:
                    config.get(section, k)
                except ConfigParser.NoOptionError:
                    config.set(section, k, v)
            else:
                config.add_section(section)
                config.set(section, k, v)
    return config

def main():         
    config = ConfigParser.ConfigParser()
    config.read(sys.path[0] + '/trustserver.cfg')
    config = check_defaults(config)

    log = Logger(sys.path[0] + '/log4py.conf').get_instance()
    log.get_root().set_loglevel(LOGLEVEL_DEBUG)
    log.get_root().set_target(sys.path[0] + '/log/tserver.log')
    log.get_root().info("Server Started")
    t = TrustServer(config, {})
    thread.start_new(t.startUpdateListener, ('',) )
    thread.start_new(t.startQueryListener, ('',) )
    # I don't know a better way to keep this from exiting, except maybe to fork 
    # new processes of the above, and then exit.:
    while 1:
        time.sleep(240)
    sys.exit(0)    

if __name__ == "__main__":
    if "--daemonize" in sys.argv:
        # do the double-fork trick     
        # see if I'm already started
        # if so, just exit.
        log = Logger(sys.path[0] + '/log4py.conf').get_instance()
        try:
            os.mkdir(os.path.dirname(PIDFILE))
        except OSError:
            pass
        #pids = open(PIDFILE, 'r').read()
        (stdin, stdout, stderr) = os.popen3("ps aux | grep `cat %s` | grep -v grep" % PIDFILE)
        stdin.close()
        stderr.close()
        pid = stdout.read().rstrip()
        stdout.close()
        if (len(pid) > 0):
        # I've already started
            log.error("TrustServer already running.  Exiting.")
            print >> stderr, "TrustServer already running.  Exiting."
            sys.exit(1)
    
        # double-fork to prevent zombie processes
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            log.error("Fork #1 failed: %d (%s)" % (e.errno, e.strerror))
            print >> stderr, "Fork #1 failed: %d (%s)" % (e.errno, e.strerror)
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
            log.error("Fork #2 failed: %d (%s)" % (e.errno, e.strerror))
            print >> stderr, "Fork #2 failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)
  
    
        #try:
        #  os.mkdir(os.path.dirname(LOGFILE))
        #except OSError:
        #   pass
        #sys.stdout = sys.stderr = Log(open(LOGFILE, 'a+'))
  
    # start the daemon main loop  
    main()

