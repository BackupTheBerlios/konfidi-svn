class TrustPath:
	"""This is a class for representing trust paths.
	Don't quite know how I'll do it, yet.
	for now, we'll use a tuple-based stack"""
	def __init__(self, data=None,path=()):
		print "creating new TrustPath: (%s, %s)" % (data, path)
		if data == None:
			self.path = path
		else:
			self.path = (data, path)
	def append(self, data):
		self.path = (data, self.path)
	def pop(self):
		# Use tuple unpacking - popping an empty FIFO will
		# raise a ValueError, which is OK
		(ret, self.path) = self.path
		return ret
	def isEmpty(self):
		if self.path == ():
			return 1
		else:
			return 0
	def reverseList(self):
		l = []
		while 1:
			try:
				(ret, self.path) = self.path
				l.insert(0, ret)
			except (ValueError):
				print "nooo!  value error!"
		return l
	def __repr__(self):
		return "%s, %s" % self.path
	
class PathNotFoundError(Exception):
	def __init__(self, source, sink, subject):
		self.source = source
		self.sink = sink
		self.subject = subject
	def __str__(self):
		return repr("%s, %s, %s" % (self.source, self.sink, self.subject))
		
class ListSubclassFifo(list):
    __slots__ = ('back',)
    def __init__(self):
        self.back = []
    def enqueue(self, elt):
        self.back.append(elt)
    def dequeue(self):
        if self:
            return self.pop()
        else:
            self.back.reverse()
            self[:] = self.back
            self.back = []
            return self.pop()
 
class Fifo(object):
	__slots__ = ('data',)
	def __init__(self):
		self.data = [[], []]
	def __init__(self, head=None, path=None):
		if path == None:
			self.data = [[], []]
		else:
			self.data = path
		self.append(head)
	def append(self, value):
		self.data[1].append(value)
	def pop(self,n=-1):
		d = self.data
		if not d[0]:
			d.reverse()
			d[0].reverse()
		return d[0].pop()
	
