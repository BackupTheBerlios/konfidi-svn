import sys
from socket import *
serverHost = 'localhost'
serverPort = 50010

if len(sys.argv) > 1:
	serverHost = sys.argv[1]
	if len(sys.argv) > 2:
		serverPort = int(sys.argv[2])
		if len(sys.argv) > 3:
			filename = sys.argv[3]

print "Connecting to %s on port %i" % (serverHost, serverPort)

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))

if filename:
	sockobj.send(filename)
else:
	print "Connected!  Please enter message."
	while 1:
		line = sys.stdin.readline()
		if line.rstrip() == "EOF": break
		sockobj.send(line)
sockobj.close()