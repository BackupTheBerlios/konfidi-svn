import dump
from mod_python import apache

import os
import re

def uniqueURI(req):
    """Returns the URI portion unique to this request, disregarding the domain, real directory, etc"""
    req.add_common_vars()
    uri = req.filename[len(os.path.dirname(__file__))+1:]
    try:
        uri += req.subprocess_env['PATH_INFO']
    except KeyError:
        uri += ""
    return uri


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

def index(req):
    req.content_type = "text/html"
    req.write('<a href="test">test output</a><br>')
    req.write('<br>')
    req.write('<a href="form">web form</a><br>')
    req.write('<br>')
    req.write('<a href="123">sample: andy schamp</a><br>')
    req.write('<a href="EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70">sample w/ sig: dave brondsema</a><br>')
    return apache.OK

def get(req):
    uri = uniqueURI(req)
    # security check, allow hex only
    if re.search('^[A-F0-9]*$', uri):
        filename = os.path.join(os.path.dirname(__file__), req.get_options()['storage.dir.xml'], uri + '.rdf')
        filename_asc = os.path.join(os.path.dirname(__file__), req.get_options()['storage.dir.pgp'], uri + '.rdf')
        try:
            try:
                req.content_type = "text/plain"
                sigfile = open(filename_asc + '.asc', 'r')
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

def storefoaf(content):
    pass
    
def put(req):
    return apache.HTTP_NOT_IMPLEMENTED

# URL-unescape (from http://c2.com/cgi/wiki?QueryStringParserTranslations)
def urldecode(astring):
    return re.sub('%(..)', lambda mo: chr(int(mo.group(1), 16)), astring.replace('+', ' '))

def form(req):
    req.content_type = "text/html"
    req.write("""
    <html>
    <head><title>FOAFServer upload form</title></head>
    <body>""")
    
    if (req.method == "POST"):
        # get just this argument
        content = req.read()
        content_start = len("foaf_content=")
        content_end = content.find("&")
        content = content[content_start:content_end]
        
        storefoaf(urldecode(content))
        req.write("<p>FOAF succesfully uploaded</p>")
    
    req.write("""<form action="form" method="POST">
    Submit an unsiqned FOAF record:<br/>
    <textarea name="foaf_content" rows="20" cols="50" wrap="none"></textarea>
    <br/>
    <input type="submit" name="submit" value="submit">
    </form>
    </body></html>""")
    return apache.OK

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
