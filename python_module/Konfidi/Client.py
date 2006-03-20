import email
import os
import tempfile
import GPG3
import re

konfidi_headers = ['X-PGP-Signature', 'X-PGP-Fingerprint', 'X-Konfidi-Email-Rating', 'X-Konfidi-Email-Level', 'X-Konfidi-Client']

class ContentTypeError(Exception):
    pass
    
class PublicKeyError(Exception):
    pass
    
class ValidationError(Exception):
    pass

class FromMismatchError(Exception):
    pass
    
class InvalidEmailAddressError(Exception):
    pass

def check_message(filename):
    m = email.message_from_file(open(filename))
    map(m.__delitem__, konfidi_headers)
    try:
        if m.get_content_type() != "multipart/signed":
            raise ContentTypeError(m.get_content_type())
        if m.get_payload()[1].get_content_type() != "application/pgp-signature":
            raise ContentTypeError(sig.get_content_type())
        
        sig = verify(m.get_payload()[0], m.get_payload()[1])
        email_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}').search(m['From']).group()
        if email_address is None:
            raise InvalidEmailAddressError(m['From'])
        if sig.stderr.find(email_address.group()) < 0:
            raise FromMismatchError(email.Utils.parseaddr(m['From']))
        
        konfidi_lookup(source, sig.fingerprint)
        
    except ContentTypeError:
        m['X-PGP-Signature'] = "none"
    except PublicKeyError:
        m['X-PGP-Signature'] = "public key not available"
    except ValidationError, e:
        m['X-PGP-Signature'] = "invalid: %s" % (e.error_text)
#    except InvalidEmailAddressError, i:
#        m['X-PGP-Signature'] =
    except FromMismatchError, f:
        m['X-PGP-Signature'] = "from mismatch: %s not found" % (f.address)

# done in two lines
#def match_from(fingerprint):
#    pass
    
def verify(body, sig):
    (body_fd, body_file) = tempfile.mkstemp()
    (sig_fd, sig_file) = tempfile.mkstemp()
    
    b = os.fdopen(body_fd, 'wb')        
    # need the body intact to verify it, including MIME headers
    # also, convert line endings from \n to \r\n
    b.write(re.sub("\r?\n", "\r\n", body.as_string()))
    b.close()
    
    s = os.fdopen(sig_fd, 'wb')
    # need the payload of the sig without its MIME headers
    s.write(sig.get_payload())
    s.close()
    
    g = GPG3.GPG("c:\\GnuPG\\gpg.exe")
    sig = g.verify_detached(body_file, sig_file)
    
    #print body_file
    #print sig_file
    os.remove(body_file)
    os.remove(sig_file)
    return sig

def match_from(email, fingerprint):
    pass
    
def konfidi_lookup(source, sink):
    pass
