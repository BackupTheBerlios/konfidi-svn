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

from random import randint

class SignedFOAF:
    """a PGP-signed FOAF document"""
    
    def __init__(self, foaf, signature, accept_types=None):
        self.foaf = foaf
        self.signature = signature
        self.accept_types = accept_types
        
        self.mimetype = None
        self.mimesubtype = None
        
        if accept_types is not None:
            # ignore q-values; for now we'll set preference
            if accept_types.find("multipart/signed") != -1:
                self.mimetype = "multipart/signed"
                for type in ["application/xml+rdf", "text/xml", "text/*", "application/xml"]:
                    if accept_types.find(type) != -1:
                        self.mimesubtype = type
                        break
            else:
                for type in ["application/pgp-signature", "application/xml+rdf", "text/xml", "text/*", "application/xml"]:
                    if accept_types.find(type) != -1:
                        self.mimetype = type
                        break
        # cleanup
        if self.mimetype is None:
            self.mimetype = "text/xml"
        elif self.mimetype == "text/*":
            self.mimetype = "text/xml"
        elif self.mimetype == "multipart/signed":
            if self.mimesubtype == "text/*":
                self.mimesubtype = "text/xml"
            elif self.mimesubtype is None:
                self.mimesubtype = "application/xml+rdf"
        
        range = 1000000000
        self.boundary = '-------' + str(randint(1*range,9*range))
        
        self.micalg = 'pgp-sha1'
    
    def verify_sig(self):
        return self.signature.verify(self.foaf.content)

    def return_mimetype(self):
        return self.mimetype
    
    def content_type(self):
        if self.mimetype == "multipart/signed":
            return 'multipart/signed; boundary="' + self.boundary + '"; protocol="application/pgp-signature"; micalg=' + self.micalg
        else:
            return self.mimetype

    def body(self):
        # TODO: PGP-ascii wrap signature option?

        if self.mimetype == "multipart/signed":
            return self.boundary + "\n" + "Content-Type: " + self.mimesubtype + "\n\n" + self.foaf.content + "\n" + self.boundary + "\nContent-Type: application/pgp-signature\n\n" + self.signature.content + self.boundary + "\n"
            
        elif self.mimetype == "application/pgp-signature":
            return self.signature.content
            
        elif self.mimetype == "application/xml":
            return self.foaf.content
        elif self.mimetype == "application/xml+rdf":
            return self.foaf.content
        elif self.mimetype == "text/xml":
            return self.foaf.content
            
        else: # text/plain
            return self.foaf.content