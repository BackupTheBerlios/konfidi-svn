import time
import SocketServer
import thread
import sys

#myHost = ''
#updatePort = 50000
#requestPort = 50010

def openAnything(source):
    if source == "-":
		import sys
		return sys.stdin
		
    # try to open with urllib (if source is http, ftp, or file URL)
    import urllib                         
    try:                                  
        return urllib.urlopen(source)
    except (IOError, OSError):            
        pass                              
    # try to open with native open function (if source is pathname)
    try:                                  
        return open(source)
    except (IOError, OSError):            
        pass                              
    # treat source as string
    import StringIO                       
    return StringIO.StringIO(str(source))

class UpdateListener(SocketServer.BaseRequestHandler):
	def handle(self):
		print "update connection!"
		str = ''
		while 1:
			data = self.request.recv(1024)
			if not data: break
			str += data
		self.request.close()
		self.load(openAnything(str))
		print "update connection closed."
	def load(self, source):
		print "UpdateListener: parsing input"
		dir(source)
		print source
		pass
			
class QueryListener(SocketServer.BaseRequestHandler):
	def handle(self):
		print "query connection!"
		while 1:
			data = self.request.recv(1024)
			if not data: break
			self.request.send("Que: %s\n" % (data))
		self.request.close()
		print "query connection closed."
	
class TrustServer:	
	def __init__(self, host='', updatePort=50010, queryPort=50000):
		self.host = host
		self.updatePort = updatePort
		self.queryPort = queryPort
		self.people = {}
		self.updateListener = SocketServer.ThreadingTCPServer((self.host, self.updatePort), UpdateListener)
		self.queryListener = SocketServer.ThreadingTCPServer((self.host, self.queryPort), QueryListener)
		
	def startUpdateListener(self, junk):
		print "Starting Update Listener"
		self.updateListener.serve_forever()
		
	def startQueryListener(self, junk):
		print "Starting Update Listener"
		self.queryListener.serve_forever()

if __name__ == "__main__":	
	print "Server Started"	
	t = TrustServer('', 50010, 50000)
	thread.start_new(t.startUpdateListener, ('',) )
	thread.start_new(t.startQueryListener, ('',) )
	time.sleep(5)
	print "Server running.  Enter commands below: "
	while 1:
		junk = sys.stdin.readline()
		print junk
		if junk.rstrip() == "quit": sys.exit(0)
	