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

from TrustPath import TrustPath
from TrustPath import PathNotFoundError
from TrustPath import Fifo
from TrustPathFinder import ReadOnly
import xmlgen

class PrototypeTPF(ReadOnly):
	def do_query(self, source, sink, opts):
		f = xmlgen.Factory()
		options = {}
		xmlopt = []
		# split the list of options, and build a dictionary out of it
		for o in opts.split("|"):
			(k, v) = o.split("=")
			options[k] = v
		
		path = self.findPath(source, sink, options["subject"])
		pathstr = "%s" % path
		rating = self.getPathRating(path, options["subject"])
		
		trustresult = f.trustresult[f.rating("%s" % rating), f.path(pathstr)]
		t = str(trustresult)
		return "%s" % (t)
	
	def findPath(self, source, sink, subject):
		#print "searching for: %s to %s regarding %s" % (source, sink, subject)
		paths = {}
		seen = {source:1}
		newpaths = { source:list([u"%s" % source]) }
		length = 0
		didsomething = 1
		while sink not in seen and didsomething:
			#high limit for now, but do we really need it?
			if length > 30:
				raise PathNotFoundError(source, sink, subject)
			
			# keep only the longest paths.
			paths = newpaths
			newpaths = {}
			for p in paths:
				# save the current path
				curpath = paths[p]
				# for each child of p
				didsomething = 0
				for s in self.people[p].trusts:
					if s not in seen:
						didsomething = 1
						try:
							if (subject in self.people[p].trusts[s]) or ("default" in self.people[p].trusts[s]):
								# mark child as seen
								seen[s] = 1
								# add new path ending in child to path dict
								t = list(curpath)
								t.append(s)
								newpaths[s] = t
						except KeyError, k:
							print "error: %s" % (k)
			length += 1
			
		paths = newpaths
		return paths[sink]
	
	def getRating(self, source, sink, subject):
		"""This function assumes that there is in fact a 
		connection between the source and the sink.  This
		ought to be established, though, in the findPath stage."""
		#print "getRating: %s -> %s" % (source, sink)
		if subject in self.people[source].trusts[sink]:
			rating = self.people[source].trusts[sink][subject]
		else: 
			rating = self.people[source].trusts[sink]["default"]
		#print "\trating: %s" % rating
		return rating
	
	def getPathRating(self, path, subject):
		source = path.pop(0)
		sink = path.pop(0)
		rating = self.getRating(source, sink, subject)
		while (len(path) > 0):
			source = sink
			sink = path.pop(0)
			rating = .5-(.5-rating)*self.getRating(source, sink, subject)
		#print "total rating: %s" % rating
		return rating
