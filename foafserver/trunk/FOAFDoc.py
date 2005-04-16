import os
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
        TRUST = Namespace("http://brondsema.gotdns.com/svn/dmail/schema/trunk/trust.owl#")
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
            fingerprint = store.objects(truster, WOT["fingerprint"]).next()
            if last_fingerprint:
                if fingerprint != last_fingerprint:
                    raise FOAFServerError, "All 'wot:fingerprint's from 'trust:truster's must be the same.  Found '%s' and '%s'" % (fingerprint, last_fingerprint)
            last_fingerprint = fingerprint
        
        fingerprint = fingerprint.replace(" ", "")
        fingerprint = fingerprint.replace(":", "")
        if require_hex_fpr and not(ishex(fingerprint)):
            raise FOAFServerError, "Invalid fingerprint format; must be hex"
        
        if uri_fingerprint and uri_fingerprint != fingerprint:
            raise FOAFServerError, "URI fingerprint doesn't match FOAF fingerprint"
            
        return fingerprint