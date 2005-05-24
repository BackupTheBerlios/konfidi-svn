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
from pyme import core, callbacks
from pyme.constants.sig import mode

from FOAFServerError import FOAFServerError

class PGPSig:
    """A PGP signature"""
    
    def __init__(self, content=None):
        self.content = content
        self.ctx = core.Context()

    def load(self, dir, fingerprint):
        """ open, read, close """
        filename = os.path.join(os.path.dirname(__file__), dir, fingerprint + '.rdf.asc')
        infile = open(filename, 'r')
        self.content = infile.read()
        infile.close()
        return

    def save(self, dir, fingerprint):
        """ open, write, close """
        filename = os.path.join(os.path.dirname(__file__), dir, fingerprint + '.rdf.asc')
        out = open(filename, 'w')
        out.write(self.content)
        out.close()
        return filename
    
    def verify(self, signed_text):
        """verify this signature against some plaintext"
        #self.content = open("/home/ams5/foafs/EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70.rdf.asc", 'r').read()
        #signed_text = open("/home/ams5/foafs/EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70.rdf", 'r').read()
        self.ctx.op_verify(core.Data(self.content), core.Data(signed_text), None)
        result = self.ctx.op_verify_result()
        sign = result.signatures
        index = 0
        while sign:
            index += 1
            key = self.ctx.get_key(sign.fpr, 0)
            #print "signature", index, ":"
            #print "  status:     ", sign.status
            #print "  timestamp:  ", sign.timestamp
            #print "  fingerprint:", sign.fpr
            #print "  uid:        ", key.uids.uid
            #print "  subkey:     ", key.subkeys.keyid[-8:]
            raise FOAFServerError("boo: " + sign.fpr + "|" + key.uids.uid)
            sign = sign.next
        if result.signatures is None:
            raise FOAFServerError("No PGP signature found")
        
        # List results for all signatures. Status equal 0 means "Ok".
        if result.signatures.status != 0:
            raise FOAFServerError("PGP signature is not valid")