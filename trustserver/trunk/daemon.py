#!/usr/bin/env python

###########################################################################
# configure these paths:
LOGFILE = '/home/ams5/public_html/trunk/log/trustserver.log'
PIDFILE = '/home/ams5/public_html/trunk/run/trustserver.pid'

# and let USERPROG be the main function of your project
import TrustServer 
USERPROG = TrustServer.main
###########################################################################

#based on J�rgen Hermanns http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
import sys, os

class Log:
    """file like for writes with auto flush after each write
    to ensure that everything is logged, even during an
    unexpected exit."""
    def __init__(self, f):
        self.f = f
    def write(self, s):
        self.f.write(s)
        self.f.flush()

def main():
    #change to data directory if needed
    os.chdir("/home/ams5/public_html/trunk")
    #redirect outputs to a logfile
    sys.stdout = sys.stderr = Log(open(LOGFILE, 'a+'))
    # redirect input from a named pipe
    #os.open('/tmp/trustpipe', os.O_RDONLY) 
    #sys.stdin = open('/tmp/trustpipe', 'r')
    #ensure the that the daemon runs a normal user
    os.setegid(100)     #set group first "pydaemon"
    os.seteuid(1008)     #set user "pydaemon"
    #start the user program here:
    USERPROG()

if __name__ == "__main__":
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
    main()
