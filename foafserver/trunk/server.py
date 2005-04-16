from mod_python import apache

# local
import dump
from MultipartSigned import MultipartSigned
from PGPSig import PGPSig
from FOAFDoc import FOAFDoc
from FOAFServerError import FOAFServerError

# system
import os
import re
import sys
from socket import *
from mod_python import apache
from mod_python import util

foafserver_version = "0.1"


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

def handler(req):
    """main handler; called by mod_python"""
    req.allow_methods(["GET", "PUT"])
    
    if req.get_config().has_key('PythonDebug'):
        reload(dump)
        from MultipartSigned import MultipartSigned
        from PGPSig import PGPSig
        from FOAFDoc import FOAFDoc
        from FOAFServerError import FOAFServerError
    
    if (uniqueURI(req) == "test"):
        return test(req)
    elif (uniqueURI(req) == "form"):
        return form(req)
    elif (uniqueURI(req) == ""):
        return index(req)
    elif (uniqueURI(req) == "weird"):
        req.status = apache.HTTP_NOT_IMPLEMENTED
        req.content_type = "text/html"
        req.write("501: we can't do that yet!")
        return apache.OK
    elif (req.method == "GET"):
        return get(req)
    elif (req.method == "PUT"):
        return put(req)
    return apache.OK

#
# various handlers depending on the request
#

def index(req):
    req.content_type = "text/html"
    req.write("""
    <html>
    <head><title>FOAFServer</title></head>
    <body>
    <h2>FOAFServer v""" + foafserver_version + """</h2>
    
    <h4>Retrieving</h4>
    Just do a GET using a URL of the PGP fingerprint
    <br>
    <a href="8A335B856C4AE39A0C36A47F152C15A0F2454727">andy schamp</a><br>
    <a href="EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70">dave brondsema</a><br>
    
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
        try:
            try:
                sig = PGPSig()
                sig.load(req.get_options()['storage.dir.sig'], uri)
                req.write(sig.content)
            except IOError:
                req.content_type = "text/xml"
            foaf = FOAFDoc()
            foaf.load(req.get_options()['storage.dir.rdf'], uri)
            req.write(foaf.content)
            return apache.OK
        except IOError:
            apache.log_error("not found: requested " + uri, apache.APLOG_ERR)
            return apache.HTTP_NOT_FOUND
    else:
        apache.log_error("invalid: requested " + uri, apache.APLOG_ERR)
        return apache.HTTP_FORBIDDEN

def put(req):
    fingerprint = uniqueURI(req)
    content = req.read()
    err = storefoaf(req, content, fingerprint)
    
    if err:
        apache.log_error(err, apache.APLOG_NOTICE)
        req.status = apache.HTTP_NOT_ACCEPTABLE
        req.write("Error: " + err)
        return apache.OK
    else:
        return apache.OK

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


def storefoaf(req, content, uri_fingerprint=""):
    foaf = FOAFDoc(content)
    try:
        fingerprint = foaf.validate(uri_fingerprint, req.get_options()['validate.wot'] == "1")
    except FOAFServerError:
        return str(sys.exc_info()[1])
    filename = foaf.save(req.get_options()['storage.dir.rdf'], fingerprint)
    updatetrustserver(req, filename)

def updatetrustserver(req, filename):
    hostname = req.get_options()['trustserver.hostname']
    port = int(req.get_options()['trustserver.port'])
    
    sockobj = socket(AF_INET, SOCK_STREAM)
    sockobj.connect((hostname, port))
    sockobj.send(filename)
    sockobj.close()

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
    req.write("sys.path: %s\n" % sys.path)
    req.write("\n")
    req.write("POST form data:\n")
    req.write("content length: " + dump.dump(req.clength))
    req.write(dump.dump(req.read()))
    #req.write(dump.dump(apache.config_tree()))
    
    return apache.OK
