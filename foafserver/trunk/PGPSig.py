import os

from FOAFServerError import FOAFServerError

class PGPSig:
    """A PGP signature"""
    
    def __init__(self, content=None):
        self.content = content

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
