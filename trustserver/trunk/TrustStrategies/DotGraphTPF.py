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
from TrustPath import Fifo
from TrustPathFinder import ReadOnly
import pydot
import xmlgen
import pickle

class DotGraphTPF(ReadOnly):
	debug = True
	def do_query(self, source, sink, options):
		res = """
		digraph konfidi {
			edge [fontsize = 8]
			node [shape = circle, style=filled, fillcolor=lightsteelblue1, fixedsize=true, height=0.5, width=0.5, fontsize=8];
			"""
		for (k, v) in self.people.items():
			for (trusted, items) in self.people[k].trusts.items():
				val = 0.0
				count = 0.0
				for (topic, rating) in items.items():
					val += float(rating)
					count += 1
				res += "%s -> %s [ label = \"%s\" ];\n" % (v.fingerprint[-8:], trusted[-8:], str(val/count))
		res += "\n}"		

		t = str(res)	
		g = pydot.graph_from_dot_data(t)
		
		return "%s" % pickle.dumps(g, pickle.HIGHEST_PROTOCOL)

