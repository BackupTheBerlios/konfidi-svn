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

# so no-one uses this strategy by accident.  remove this comment and the following line.
raise Error

# you must choose either
from TrustPathFinder import ReadOnly
# or
from TrustPathFinder import ReadWrite
# as the parent class depending on what your strategy is to do.  Read-only strategies use
# the server's read lock, and so are more responsive.  Read-write strategies use the server's
# read-write lock, and so must wait for all readers to finish before proceeding.  By making a 
# read-only strategy, you are agreeing not to modify the data in the trust network.  Doing 
# otherwise could create real problems.

# This library is used to generate the XML response that will be parsed by the QueryListener
import xmlgen

class StrategyName(ReadOnly): # or class StrategyName(ReadWrite):

	# the do_query method receives the source and sink from the parent class, and returns the 
	# result in XML.  any options that are passed to the strategy in the query will be in the 
	# dictionary 'self.options', indexed by key.
	def do_query(self, source, sink):
		f = xmlgen.Factory()

		# find the result however you'd like, analyze the data, or whatever, and assign 
		# it as a string (possibly a pickled object)
		result = "foobar"
		
		# package the result so that it can be parsed properly by the outer layers
		trustresult = f.trustresult[f.data(result)]

		# sometimes it isn't converted to a string properly.  who knows why?
		t = str(trustresult)
		return "%s" % t

