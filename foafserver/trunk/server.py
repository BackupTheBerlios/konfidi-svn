# local
import dump

# system
import os
import re
import sys
from rdflib.Namespace import Namespace
from rdflib.TripleStore import TripleStore
from rdflib.StringInputSource import StringInputSource
from xml.sax import SAXParseException
from mod_python import apache
from mod_python import util

# our own error class
class FOAFServerError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#
# Simple utility functions
#

def uniqueURI(req):
    """Returns the URI portion unique to this request, disregarding the domain, real directory, etc"""
    req.add_common_vars()
    uri = req.filename[len(os.path.dirname(__file__))+1:]
    try:
        uri += req.subprocess_env['PATH_INFO']
    except KeyError:
        uri += ""
    return uri

def ishex(string):
    return re.search('^[A-F0-9]+$', string)

#
# main handler; called by mod_python
#
def handler(req):
    req.allow_methods(["GET", "PUT"])
    
    if req.get_config().has_key('PythonDebug'):
        reload(dump)
    
    if (uniqueURI(req) == "test"):
        return test(req)
    if (uniqueURI(req) == "form"):
        return form(req)
    if (uniqueURI(req) == ""):
        return index(req)
    elif (req.method == "GET"):
        return get(req)
    elif (req.method == "PUT"):
        return put(req)
    else:
        return apache.HTTP_NOT_IMPLEMENTED

#
# various handlers depending on the request
#

def index(req):
    req.content_type = "text/html"
    req.write("""
    <html>
    <head><title>FOAFServer</title></head>
    <body>
    <h2>FOAFServer</h2>
    
    <h4>Retrieving</h4>
    Just do a GET using a URL of the PGP fingerprint
    <br>
    <a href="123">sample: andy schamp</a><br>
    <a href="EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70">sample w/ sig: dave brondsema</a><br>
    
    <h4>Uploading</h4>
    Human web interface: <a href="form">web form</a><br>
    Programmatic interface: Just do a PUT using a URL of the PGP fingerprint (much like retrieving)
    
    <h4><a href="test">debug output</a></h4>
    </body>
    </html>
    """)
    return apache.OK

def get(req):
    uri = uniqueURI(req)
    # security check, allow hex only
    if ishex(uri):
        filename = os.path.join(os.path.dirname(__file__), req.get_options()['storage.dir.rdf'], uri + '.rdf')
        filename_asc = os.path.join(os.path.dirname(__file__), req.get_options()['storage.dir.sig'], uri + '.rdf.asc')
        try:
            try:
                req.content_type = "text/plain"
                sigfile = open(filename_asc, 'r')
                req.write(sigfile.read())
                sigfile.close()
            except IOError:
                req.content_type = "text/xml"
            xmlfile = open(filename, 'r')
            req.write(xmlfile.read())
            xmlfile.close()
            return apache.OK
        except IOError:
            apache.log_error("not found: requested " + uri, apache.APLOG_ERR)
            return apache.HTTP_NOT_FOUND
    else:
        apache.log_error("invalid: requested " + uri, apache.APLOG_ERR)
        return apache.HTTP_FORBIDDEN

def put(req):
    return apache.HTTP_NOT_IMPLEMENTED

def form(req):
    req.content_type = "text/html"
    req.write("""
    <html>
    <head><title>FOAFServer upload form</title></head>
    <body>
    <a href="./">Back to index</a>
    """)
    
    if (req.method == "POST"):
        
        form = util.FieldStorage(req, 1)
        
        try:
            content = form["foaf_content"]
        except KeyError:
            if not(form["foaf_file"].filename):
                req.write("<p>You must select a file</p>")
            content=form["foaf_file"].value
        
        store_error = storefoaf(req, content)
        if store_error:
            req.write("<p>Error: " + store_error + "</p>")
        else:
            req.write("<p>FOAF succesfully uploaded</p>")
    
    req.write("""
    <h2>Submit an unsiqned FOAF record</h2>
    <form action="form" method="POST" enctype="multipart/form-data">
    Upload FOAF file: <input type="file" name="foaf_file"/>
    <input type="submit" name="submit" value="Submit">
    </form>
    <hr/>
    Or paste FOAF XML:
    <form action="form" method="POST">
    <textarea name="foaf_content" rows="20" cols="50" wrap="none"></textarea>
    <br/>
    <input type="submit" name="submit" value="Submit">
    </form>
    </body></html>""")
    return apache.OK

#
# workhorse utilities
#

# TODO: refactor this logic into something common to trustserver/UpdateListener.py too?
# TODO: what else to validate?
def validate(content):
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    TRUST = Namespace("http://brondsema.gotdns.com/svn/dmail/foafserver/trunk/schema/trust.owl")
    WOT = Namespace("http://xmlns.com/wot/0.1/")
    RDF = Namespace("http://www.w3.org/2000/01/rdf-schema")
    store = TripleStore()
    try:
        store.parse(StringInputSource(content))
    except SAXParseException:
        raise FOAFServerError, "invalid XML: " + str(sys.exc_info()[1])
    try:
        truster = store.subjects(TRUST["trusts"]).next()
    except StopIteration:
        raise FOAFServerError, "must have a trust:Truster"
    try:
        fingerprint = store.objects(truster, WOT["fingerprint"]).next()
    except StopIteration:
        raise FOAFServerError, "Truster must have a wot:fingerprint"
    if not(ishex(fingerprint)):
        raise FOAFServerError, "Invalid fingerprint format; must be hex"
    # TODO: something with fingerprint
    try:
        mbox = store.objects(truster, FOAF["mbox"]).next()
    except StopIteration:
        raise FOAFServerError, "Truster must have a foaf:mbox"
    return fingerprint

def savetofile(req, content, fingerprint):
    filename = os.path.join(os.path.dirname(__file__), req.get_options()['storage.dir.rdf'], fingerprint + '.rdf')
    foaffile = open(filename, 'w')
    foaffile.write(content)
    foaffile.close()

def storefoaf(req, content):
    try:
        fingerprint = validate(content)
    except FOAFServerError:
        return str(sys.exc_info()[1])
    err = savetofile(req, content, fingerprint)
    if err:
        return err
    pass
    

#
# test stuff; delete sometime
#

def test(req):
    req.content_type = "text/plain"
    
    apache.log_error("request!", apache.APLOG_NOTICE)
    req.write("\nParsed URI:\n-------------\n")
    req.write(dump.dump(req.parsed_uri))
    req.write("\nModPython Options:\n-------------\n")
    req.write(dump.dump(req.get_options()))
    req.write("\nModPython Config:\n-------------\n")
    req.write(dump.dump(req.get_config()))
    
    req.write("\nOS Env:\n-------------\n")
    req.write(dump.dump(os.environ))
    
    req.write("\nProcess Env:\n-------------\n")
    req.add_common_vars()
    req.write(dump.dump(req.subprocess_env))
    
    req.write("\n")
    req.write("server_root=" + apache.server_root() + "\n")
    req.write("document_root=" + req.document_root() + "\n")
    req.write("loglevel=" + dump.dump(req.server.loglevel))
    req.write("is_virtual=" + dump.dump(req.server.is_virtual))
    req.write("phase=" + dump.dump(req.phase))
    req.write("handler=" + dump.dump(req.handler))
    req.write("uri=" + dump.dump(req.uri))
    req.write("filename=" + dump.dump(req.filename))
    req.write("py interpreter=" + dump.dump(req.interpreter))
    
    req.write("\n")
    req.write("__file__=" + __file__ + "\n")
    req.write("dir=" + os.path.dirname(__file__) + "\n")
    
    req.write("\n")
    if apache.mpm_query(apache.AP_MPMQ_IS_THREADED):
        req.write("mpm is threaded\n")
    else:
        req.write("mpm is NOT threaded\n")
    if apache.mpm_query(apache.AP_MPMQ_IS_FORKED):
        req.write("mpm is forked\n")
    else:
        req.write("mpm is NOT forked\n")
        
    req.write("\n")
    req.write("POST form data:\n")    
    req.write("content length: " + dump.dump(req.clength))
    req.write(dump.dump(req.read()))
    #req.write(dump.dump(apache.config_tree()))
    
    return apache.OK
