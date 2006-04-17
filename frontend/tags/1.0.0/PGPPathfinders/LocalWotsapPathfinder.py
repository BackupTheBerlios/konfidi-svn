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

from PGPPathfinder import PGPPathfinder
import os
import locale
import imp
from StringIO import StringIO
import re

#local
import xmlgen

class LocalWotsapPathfinder(PGPPathfinder):
	"""Uses wotsap from http://www.lysator.liu.se/~jc/wotsap/ and it's nightly-generated dump file"""
	def graph(self, source, sink, limit=None):
		(out, err) = self.runwotsap(source, sink, limit)
		f = xmlgen.Factory()
		if not err:
			out = re.sub('<', '&lt;', out)
			out = re.sub('>', '&gt;', out)
			return f.pgp_result()[f.connected("1"), f.path(out), f.error()] # + err
		else:
			err = re.sub('<', '&lt;', err)
			err = re.sub('>', '&gt;', err)
			return f.pgp_result()[f.connected("0"), f.path(), f.error(err)]

	def connected(self, source, sink, limit=None):
		(out, err) = self.runwotsap(source, sink, limit)
		return out != None # and len(err) == 0

	def runwotsap(self, source, sink, limit=None):
		"""note how wotsap doesn't support a long fingerprint, so we just take the last 8 chars"""
		file = None
		mod = None
		try:
			mod = imp.load_source("Wot", self.config["app"])
		finally:
			pass
		
		# see also wotsapmain
		wot = mod.Wot(self.config["data"])
		try:
			web = wot.findpaths(source[-8:], sink[-8:], None)
		except mod.wotError, err:
			#errmsg = unicode(err).encode(encoding, 'replace')
			return (None, str(err))
		if web is None:
			return (None, "Sorry, unable to find path.")
			
		if "getpreferredencoding" in dir(locale):
			encoding = locale.getpreferredencoding()
		else:
			locale.setlocale(locale.LC_CTYPE, "")
			encoding = locale.nl.langinfo(locale.CODESET)
			
		return (wot.creategraph(web, format='txt').encode(encoding, 'replace'), None)
