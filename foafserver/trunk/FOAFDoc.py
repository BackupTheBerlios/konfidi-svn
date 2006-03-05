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

import os
import sys
from xml.sax import SAXParseException

from rdflib.Namespace import Namespace
from rdflib.TripleStore import TripleStore
from rdflib.StringInputSource import StringInputSource

from FOAFServerError import FOAFServerError

def ishex(string):
    return re.search('^[A-F0-9]+$', string)

class FOAFDoc:
    """A FOAF RDF document"""
    
    def __init__(self, content=None):
        self.content = content

    def load(self, dir, fingerprint):
        """ open, read, close """
        filename = os.path.join(os.path.dirname(__file__), dir, fingerprint + '.rdf')
        infile = open(filename, 'r')
        self.content = infile.read()
        infile.close()
        return

    def save(self, dir, fingerprint):
        """ open, write, close """
        filename = os.path.join(os.path.dirname(__file__), dir, fingerprint + '.rdf')
        out = open(filename, 'w')
        out.write(self.content)
        out.close()
        return filename

    # TODO: refactor this logic into something common to trustserver/UpdateListener.py too?
    # TODO: what else to validate?
    def validate(self, uri_fingerprint, require_hex_fpr=1):
        """validate the format of the document"""
        
        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        TRUST = Namespace("http://www.konfidi.org/ns/trust/1.2#")
        WOT = Namespace("http://xmlns.com/wot/0.1/")
        RDF = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        store = TripleStore()
    
        # TODO: verify all <truster>s have fingerprints
        # and that they're all the same
        try:
            store.parse(StringInputSource(self.content))
        except SAXParseException:
            raise FOAFServerError, "invalid XML: " + str(sys.exc_info()[1])
        
        fingerprint = last_fingerprint = None
        for (relationship, truster) in store.subject_objects(TRUST["truster"]):
            for (key) in store.objects(truster, WOT["hasKey"]):
                fingerprint = store.objects(key, WOT["fingerprint"]).next()
                if last_fingerprint:
                    if fingerprint != last_fingerprint:
                        raise FOAFServerError, "All wot:fingerprint's from trust:truster's PubKeys must be the same.  Found '%s' and '%s'" % (fingerprint, last_fingerprint)
                last_fingerprint = fingerprint
        
        # per http://xmlns.com/wot/0.1/, we really shouldn't replace these
        fingerprint = fingerprint.replace(" ", "")
        fingerprint = fingerprint.replace(":", "")
        if require_hex_fpr and not(ishex(fingerprint)):
            raise FOAFServerError, "Invalid fingerprint format; must be hex"
        
        if uri_fingerprint and uri_fingerprint != fingerprint:
            raise FOAFServerError, "URI fingerprint doesn't match FOAF fingerprint"
            
        return fingerprint