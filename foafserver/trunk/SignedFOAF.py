from random import randint

class SignedFOAF:
    """a PGP-signed FOAF document"""
    
    def __init__(self, foaf, signature, accept_types):
        self.foaf = foaf
        self.signature = signature
        self.accept_types = accept_types
        
        self.mimetype = None
        self.mimesubtype = None
        
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
    
    def return_mimetype(self):
        return self.mimetype
    
    def content_type(self):
        if self.mimetype == "multipart/signed":
            return 'multipart/signed; boundary="' + self.boundary + '"; protocol="application/pgp-signature"; micalg=pgp-sha1'
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