from random import randint

class MultipartSigned:
    

    """a multipart/signed MIME entity"""
    def __init__(self, body, signature, ):
        self.body = body
        self.signature = signature
        
        range = 1000000000
        self.boundary = '-------' + randint(1*range,9*range)
        
    def getContentType(self):
        return 'multipart/signed; boundary="' + self.boundary + '"; protocol="application/pgp-signature"; micalg=pgp-sha1'
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