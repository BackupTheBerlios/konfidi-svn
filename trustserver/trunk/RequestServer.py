import SocketServer
import Person

class RequestServer(SocketServer.ThreadingTCPServer):
	"""This class allow everyone to have access to the 
	people lookup table"""
	def __init__(self, server_address, RequestHandlerClass, people=None, lock=None, config=None):
		self.people = people
		self.lock = lock
		self.config = config
		SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)
		
	def getPerson(self, fingerprint):
		"""Get a person for a given fingerprint 
		if one exists, otherwise, create one."""
		# the lock stuff should make it thread safe
		#self.lock.acquire_read()
		if fingerprint in self.people:
			p = self.people[fingerprint]
		else:
			p = Person.Person(fingerprint)
			#self.lock.release_read()
			#self.lock.acquire_write()
			self.people[fingerprint] = p
			#self.lock.release_write()
			#self.lock.acquire_read()
		#self.lock.release_read()
		return p