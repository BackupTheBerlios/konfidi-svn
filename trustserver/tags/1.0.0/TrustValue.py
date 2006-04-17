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

class TrustValue:
	trustValues = { \
	"trustsCompletely":None, "trustsHighly":None, \
	"trustsAveragely":None, "trustsMinimally":None, \
	"trustsNeutrally":None, "distrustsMinimally":None, \
	"distrustsAveragely":None, "distrustsHighly":None, \
	"distrustsCompletely":None }
	
	"""represents the level of trust.  might just be an int."""
	def __init__(self, value=None):
		self.value = value
#		raise NotImplementedError
		
	def getNumericValue(self):
		raise NotImplementedError
		
	def getValue(self):
		return self.value
		
	def setValue(self, value):
		self.value = value
		
	def __repr__(self):
		return "%s" % (self.value)
	
	def aggregate(self):
		raise NotImplementedError
		
	def concatenate(self):
		raise NotImplementedError