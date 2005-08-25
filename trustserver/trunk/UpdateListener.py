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

from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.constants import TYPE
from rdflib.TripleStore import TripleStore
from rdflib.constants import DATATYPE
import SocketServer
import operator
import time
from TrustValue import TrustValue
from BasicTrustValue import BasicTrustValue
import re

from log4py import Logger
#from pickle import dumps

#local
#from dump import dump

class UpdateListener(SocketServer.BaseRequestHandler):
	def setup(self):
		# Create a namespace object for the Friend of a friend namespace.
		# figure out trailing pound thing...
		#self.FOAF = Namespace(self.server.config.foaf_url + "#")
		#self.TRUST = Namespace(self.server.config.trust_url + "#")
		#self.WOT = Namespace(self.server.config.wot_url + "#")
		#self.RDF = Namespace(self.server.config.rdf_url + "#")
		
		self.FOAF = Namespace("http://xmlns.com/foaf/0.1/")
		self.TRUST = Namespace("http://svn.berlios.de/viewcvs/*checkout*/konfidi/schema/trunk/trust.owl#")
		self.WOT = Namespace("http://xmlns.com/wot/0.1/")
		self.RDF = Namespace("http://www.w3.org/2000/01/rdf-schema#")
		
		self.log = Logger().get_instance(self)
		# load trust values into list for later
		#trust = TripleStore()
		#trust.load(self.server.config.trust_url)
		
		#trust.load("http://svn.berlios.de/viewcvs/*checkout*/konfidi/schema/trunk/trust.owl#")
		#self.trustValues = []
		#for s in trust.subjects(self.RDF["subPropertyOf"], self.TRUST["trustValue"]):
		#	self.trustValues.append(s)
			
	def handle(self):
		#print "update connection opened."
		#print "FOAF: %s" % (self.FOAF)
		#print "TRUST: %s" % (self.TRUST)
		#print "WOT: %s" % (self.WOT)
		#print "RDF: %s" % (self.RDF)
		str = ''
		while 1:
			data = self.request.recv(1024)
			if not data: break
			str += data
		self.request.send("Ok.")
		self.request.close()
		self.load(str)
		#self.load(openAnything(str))
		#print "update connection closed."
		
	def load(self, source):	
		self.log.info("Parsing input: %s" % source)
		# this is the main object we're concerned with
		trust = TripleStore()
		trust.load(source)	
		# new version
		count = 0
		for (relationship, truster) in trust.subject_objects(self.TRUST["truster"]):
			#print "r: %s, t: %s" % (relationship, truster)
			# clean up the fingerprints
			source_fingerprint = trust.objects(truster, self.WOT["fingerprint"]).next()
			sink_fingerprint = trust.objects(trust.objects(relationship, self.TRUST["trusted"]).next(), self.WOT["fingerprint"]).next()
			# turn these off for now, for our test cases.  figure a better solution later
			source_fingerprint = re.sub(r'[^0-9A-Z]', r'', source_fingerprint.upper())
			sink_fingerprint = re.sub(r'[^0-9A-Z]', r'', sink_fingerprint.upper())
			source = self.server.getPerson(source_fingerprint)
			sink = self.server.getPerson(sink_fingerprint)
			#print "sf: %s, sif: %s" % (source_fingerprint, sink_fingerprint)
			for item in trust.objects(relationship, self.TRUST["about"]):
				#print "i: %s" % item
				topic = trust.objects(item, self.TRUST["topic"]).next().split("#")[1]
				rating = float(trust.objects(item, self.TRUST["rating"]).next())
				if rating >= 0.0 and rating <= 1.0:
					source.addTrustLink(sink.getFingerprint(), topic, rating)
					count += 1
		self.log.info("Added %d trust links." % count)
		
