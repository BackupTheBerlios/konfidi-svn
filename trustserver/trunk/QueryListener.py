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

#system
import SocketServer
from log4py import Logger
#import string
import time
#import imp
#from xml.dom import minidom

#local
import xmlgen
from TrustPath import PathNotFoundError
from TrustStrategies.TrustPathFinder import InvalidPasswordError

class SourceSinkSameError(Exception):
	def __init__(self, source):
		self.source = source
	
	def __str__(self):
		return repr("%s" % (self.source))

class QueryListener(SocketServer.BaseRequestHandler):
	def setup(self):
		self.people = self.server.people
		
	def handle(self):
		log = Logger().get_instance(self)
		f = xmlgen.Factory()
		data = self.request.recv(1024)
		try:
			[strategy,options] = data.split(":")
			log.info("Executing query: %s, %s" % (strategy, options))
			
			try:
				exec("import TrustStrategies.%s " % (strategy))
				exec("debug_module = (TrustStrategies.%s.%s.debug)" % (strategy, strategy))
				if debug_module:
					exec("reload(TrustStrategies.%s) " % (strategy))
				exec("tpf = TrustStrategies.%s.%s(self.server)" % (strategy, strategy))
				
			except (ImportError), i:
				from TrustStrategies.DefaultTPF import DefaultTPF
				tpf = DefaultTPF(self.server)
				log.warning("Caught ImportError: %s\nUsing DefaultTPF strategy." % (i))
			searchtime = time.time()
			r = tpf.query(options)
			searchtime = "%.6f" % (time.time() - searchtime)
			# build the xml response
			result = f.queryresult(r, executed="1", strategy=strategy, search_time=searchtime)
			
			
		except KeyError, k:
			result = f.queryresult[f.rating(str(-1)), f.error("Person %s not found in dataset" % (k))]
		except PathNotFoundError, p:
			result = f.queryresult[f.rating(str(-1)), f.error("No path found from source to sink: %s" % (p))] 
		except SourceSinkSameError, s:
			result = f.queryresult[f.rating(str(1)), f.error("The source and the sink are the same: %s" % (s))]
		except InvalidPasswordError, i:
			result = f.queryresult[f.rating(str(-1)), f.error("Invalid password: %s" % (i))]
		#except (ValueError):
		#	self.request.send("Invalid query")
	
		r = str(result)
		# check to see if we need to make this smarter/bigger
		self.request.send("%s" % r)
		self.request.close()
	
