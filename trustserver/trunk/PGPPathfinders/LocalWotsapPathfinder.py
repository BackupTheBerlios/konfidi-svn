from PGPPathfinder import PGPPathfinder
import os

class LocalWotsapPathfinder(PGPPathfinder):
    """Uses wotsap from http://www.lysator.liu.se/~jc/wotsap/ and it's nightly-generated dump file"""
    
    def graph(self, source, sink, limit=None):
        (out, err) = self.runwotsap(source, sink, limit)
        return err + out

    def connected(self, source, sink, limit=None):
        (out, err) = self.runwotsap(source, sink, limit)
        return len(out) != 0 and len(err) == 0

    def runwotsap(self, source, sink, limit=None):
        """note how wotsap doesn't support a long fingerprint, so we just take the last 8 chars"""
        (stdin, stdout, stderr) = os.popen3("python %s -w %s %s %s" % (config.LocalWotsapPathfinder_app, config.LocalWotsapPathfinder_data, source[-8:], sink[-8:]))
        stdin.close()
        out = stdout.read()
        err = stderr.read()
        return (out, err)