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
	
