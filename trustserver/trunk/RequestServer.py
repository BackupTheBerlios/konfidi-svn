import SocketServer
import Person

class RequestServer(SocketServer.ThreadingTCPServer):
	"""This class allow everyone to have access to the 
	people lookup table"""
	def __init__(self, server_address, RequestHandlerClass, people=None):
		self.people = people
		SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)
		
	def getPerson(self, fingerprint):
		"""Get a person for a given fingerprint 
		if one exists, otherwise, create one."""
		if fingerprint in self.people:
			p = self.people[fingerprint]
		else:
			p = Person.Person(fingerprint)
			self.people[fingerprint] = p
		return p