# local
import dump

# system
import os
import re
import sys
from socket import *
#from rdflib.Namespace import Namespace
#from rdflib.TripleStore import TripleStore
#from rdflib.StringInputSource import StringInputSource
#from xml.sax import SAXParseException
from mod_python import apache
from mod_python import util

frontend_version = "0.1"

# our own error class
class FrontendError(Exception):
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


def handler(req):
    """main handler; called by mod_python"""
    req.allow_methods(["GET"])
    
    if req.get_config().has_key('PythonDebug'):
        reload(dump)
    
    if (uniqueURI(req) == "test"):
    	return test(req)
    if (uniqueURI(req) == "query"):
        return get(req)
    if (uniqueURI(req) == "form"):
        return form(req)
    if (uniqueURI(req) == ""):
        return index(req)
    #elif (req.method == "GET"):
    #    return get(req)
    else:
		return apache.HTTP_NOT_IMPLEMENTED

#
# various handlers depending on the request
#

def index(req):
	req.content_type = "text/html"
	req.write("""
    <html>
    <head><title>TrustServer Frontent</title></head>
    <body>
    <h2>TrustServer Frontend v""" + frontend_version + """</h2>
    
    <h4>Querying</h4>
    Just do a GET using to the url "query", defining the variables "source", "sink", and "subject"
    <br>
    <!--<a href="123">sample: andy schamp</a><br>
    <a href="EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70">sample w/ sig: dave brondsema</a><br>
    -->
    <h4>Web interface</h4>
    Or use <a href="form">this form</a><br>
    
    <h4><a href="test">debug output</a></h4>
	</body>
	</html>
	""")
	return apache.OK

def get(req):	
    if (req.method == "POST" or req.method == "GET"):
        form = util.FieldStorage(req, 1)
        source = form["source"]
        sink = form["sink"]
        subject = form["subject"]
    else:
		# hmm, something went wrong.
        req.write("Error 41093.");
    	 	  
	# first, check the PGP server:
	pass    	
	# then, check the TrustServer:
	sockobj = socket(AF_INET, SOCK_STREAM)
	sockobj.connect((req.get_options()['trustserver.host'], req.get_options()['trustserver.port']))
	sockobj.send("%s:%s:%s" % (source, sink, subject))
	result = "krang"
	result += "foo"
	krang = "junk"
	while 1:
		data = sockobj.recv(1024)
		if not data: break
		result += data 	
		krang += "ly"

    # maybe deal with errors somewhere in here...
    req.write("Junkly")
    req.write(result)
    return apache.OK    

def form(req):
    req.content_type = "text/html"
    req.write("""
    <html>
    <head><title>TrustServer Query form</title></head>
    <body>
    <a href="./">Back to index</a>
    """)
    
    req.write("""
    Enter your query: <br>
    <form action="query" method="POST">
    Source: <input type="text" name="source"><br/>
    Sink: <input type="text" name="sink"><br/>
    Subject: <input type="text" name="subject"><br/>
    <br/>
    <input type="submit" name="submit" value="Submit">
    </form>
    </body></html>""")
    return apache.OK

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