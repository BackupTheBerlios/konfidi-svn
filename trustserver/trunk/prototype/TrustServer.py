import SocketServer
import thread

myHost = ''
updatePort = 50000
queryPort = 50010

class UpdateListener(SocketServer.BaseRequestHandler):
	def handle(self):
		print "update connection!"
		while 1:
			data = self.request.recv(1024)
			if not data: break
			self.request.send("Upd: %s\n" % (data))
		self.request.close()
		print "update connection closed."
			
class RequestListener(SocketServer.BaseRequestHandler):
	def handle(self):
		print "query connection!"
		while 1:
			data = self.request.recv(1024)
			if not data: break
			self.request.send("Que: %s\n" % (data))
		self.request.close()
		print "query connection closed."
	
class TrustServer:	
	def __init__(self):
		pass
		
	def startUpdateListener(self, junk):
		print "Starting Update Listener"
		updateListener = SocketServer.ThreadingTCPServer((myHost, updatePort), UpdateListener)
		updateListener.serve_forever()

if __name__ == "__main__":	
	print "Server Started"	
	t = TrustServer()
	thread.start_new(t.startUpdateListener, ('',) )
	myAddr = (myHost, queryPort)
	server = SocketServer.ThreadingTCPServer(myAddr, RequestListener)
	print "Starting Query Listener"
	server.serve_forever()