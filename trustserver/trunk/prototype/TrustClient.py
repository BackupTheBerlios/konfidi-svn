import sys
from socket import *
serverHost = 'localhost'
serverPort = 50000

message = ['Default message']
if len(sys.argv) > 1:
	serverHost = sys.argv[1]
	if len(sys.argv) > 2:
		serverPort = int(sys.argv[2])
		if len(sys.argv) > 3:
			message = sys.argv[3:]

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))

for line in message:
	sockobj.send(line)
	data = sockobj.recv(1024)
	print "client recieved:", `data`
	
sockobj.close()