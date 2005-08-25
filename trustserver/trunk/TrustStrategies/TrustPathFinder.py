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

class TrustPathFinder:
	# set this to 1 in a subclass, if you want to reload the module in the QueryListener (for updates) without restarting the server.
	debug = 0
	# All strategies are restricted by default, using the password specified in the configuration file.
	# To unprotect a subclasse, override the class variable 'restricted' with 'False'
	# To change the password for a subclass, override the class variable 'password' with the desired password.
	# Anyone attempting to use that strategy must enter that strategy's password to do so.
	restricted = False # disabled for now
	password = ''
	def __init__(self, server):
		self.people = server.people
		self.lock = server.lock
		self.config = server.config
		self.options = {}
		TrustPathFinder.password = self.config.strategy_password
			
	def query(self, options):
		raise NotImplementedError
	
	def do_query(self):
		raise NotImplementedError

	def __parse_cfg(self, options):
		for o in options.split("|"):
			(k, v) = o.split("=")
			self.options[k] = v
			
	def __setup(self, options):
		self.__parse_cfg(options)
		if self.__class__.restricted:
			try:
				if self.options["password"] != self.__class__.password:
					raise InvalidPasswordError(self.options["password"])
					
			except (KeyError):
				raise InvalidPasswordError()

class ReadOnly(TrustPathFinder):
	def query(self, options):
		self.__setup(options)	
		self.lock.acquire_read()
		result = self.do_query()
		self.lock.release_read()
		return result
		
class ReadWrite(TrustPathFinder):
	def query(self, options):
		self.__setup(options)
		self.lock.acquire_write()
		result = self.do_query()
		self.lock.release_write()
		return result

class InvalidPasswordError(Exception):
	def __init__(self, password=None):
		self.password = password

	def __str__(self):
		if self.password:
			return "%s" % self.password
		else:
			return "No password supplied."
														
