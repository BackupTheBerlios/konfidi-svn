import sys
from socket import *
serverHost = 'localhost'
serverPort = 20010
filename = None
if len(sys.argv) > 1:
	serverHost = sys.argv[1]
	if len(sys.argv) > 2:
		serverPort = int(sys.argv[2])
		if len(sys.argv) > 3:
			filename = sys.argv[3]

print "Connecting to %s on port %i" % (serverHost, serverPort)

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))

str = ""

if filename != None:
	sockobj.send(filename)
else:
	print "Connected!  Please enter message."
	line = sys.stdin.readline()
	sockobj.send(line.rstrip())
	while 1:
		data = sockobj.recv(1024)
		if not data: break
		str += data
	
print str
sockobj.close()
