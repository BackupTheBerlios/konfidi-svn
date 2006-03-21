import email
import os
import tempfile
import GPG3
import re

class ContentTypeError(Exception):
    pass
    
class PublicKeyError(Exception):
    pass
    
class ValidationError(Exception):
    pass

class FromMismatchError(Exception):
    def __init__(self, address):
        self.address = address
    
class InvalidEmailAddressError(Exception):
    def __init__(self, address):
        self.address = address

class Client:
    """A general purpose Konfidi Client Class"""
    def __init__(self, config):
        import GPG3
        self.gpg = GPG3.GPG("c:\\GnuPG\\gpg.exe")
    
    
    def Verify(data):
        return self.gpg.verify(data)
    
    def VerifyFile(file):
        return self.gpg.verify_file(file)
        
    def VerifyDetached(body, sig):
        return self.gpg.verify_detached(body, sig)
        
    def KonfidiLookup(source, sink, subject):
        """'source' and 'sink' are fingerprints
        'subject' is a string indicating the subject"""
        pass
        
class EmailClient(Konfidi.Client):
    headers = ['X-PGP-Signature', 'X-PGP-Fingerprint', 'X-Konfidi-Email-Rating', 'X-Konfidi-Email-Level', 'X-Konfidi-Client']
    def __init__(self, config, message):
        Konfidi.Client.__init__(self, config)
        self.message = email.message_from_string(message)
        
    def RemoveHeaders(self):
        map(m.__delitem__, self.__class__.eaders)
        
    def CheckMessage(filename):
        try:
            if m.get_content_type() != "multipart/signed":
                raise ContentTypeError(m.get_content_type())
            if m.get_payload()[1].get_content_type() != "application/pgp-signature":
                raise ContentTypeError(sig.get_content_type())
            
            sig = VerifyDetached(m.get_payload()[0], m.get_payload()[1])
            email_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}').search(m['From']).group()
            
            if email_address is None:
                raise InvalidEmailAddressError(m['From'])
            if sig.stderr.find(email_address.group()) < 0:
                raise FromMismatchError(email_address)
            
            KonfidiLookup(source, sig.fingerprint)
            
        except ContentTypeError:
            m['X-PGP-Signature'] = "none"
        except PublicKeyError:
            m['X-PGP-Signature'] = "public key not available"
        except ValidationError, e:
            m['X-PGP-Signature'] = "invalid: %s" % (e.error_text)
        except InvalidEmailAddressError, i:
            m['X-PGP-Signature'] = "from mismatch: could not parse email address: %s" % (i.address)
        except FromMismatchError, f:
            m['X-PGP-Signature'] = "from mismatch: %s not found" % (f.address)

    def VerifyDetached(body, sig):
        return Konfidi.Client.VerifyDetached(self, re.sub("\r?\n", "\r\n", body.as_string()), sig.get_payload())
    
