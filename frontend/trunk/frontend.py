# local
import dump

# system
import os
import re
import sys
import traceback
#import exceptionTools
from socket import *
#from rdflib.Namespace import Namespace
#from rdflib.TripleStore import TripleStore
#from rdflib.StringInputSource import StringInputSource
#from xml.sax import SAXParseException
from mod_python import apache
from mod_python import util
import pickle
import string

frontend_version = "0.1"

# our own error class
class FrontendError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# our main Frontend class
class Frontend:
	def __init__(self, req):
		self.req = req
		self.config = parse_config(req.get_options())

	def handle(self):
		self.req.allow_methods(["GET"])
		
		if self.req.get_config().has_key('PythonDebug'):
			reload(dump)
		
		page = uniqueURI(self.req)
		if (page == "test"):
			return self.test(self.req)
		if (page == "people"):
			return self.people(self.req)
		if (page == "query"):
			return self.query(self.req)
		if (page == "form"):
			return self.form(self.req)
		if (page == "command"):
			return self.command(self.req)
		if (page == ""):
			return self.index(self.req)
		else:
			return apache.HTTP_NOT_IMPLEMENTED
			
	#
	# various handlers depending on the request
	#
	
	def index(self, req):
		req.content_type = "text/html"
		req.write("""
		<html>
		<head><title>TrustServer Frontend</title></head>
		<body>
		<h2>TrustServer Frontend v""" + frontend_version + """</h2>
	
		<h4>Querying</h4>
		Just do a GET using to the url "query", defining the variables "source", "sink", and "subject"
		<br>
		<a href="query?strategy=Prototype&source=Schamp&sink=Crowe&subject=cooking">sample: Schamp, Crowe, cooking</a><br>
		<a href="query?strategy=Prototype&source=Brondsema&sink=Schamp&subject=dmail">sample: Brondsema, Schamp, dmail</a><br>
		<a href="query?strategy=Prototype&source=Brondsema&sink=Laing&subject=email">sample: Brondsema, Laing, email</a><br>
		<a href="query?strategy=Prototype&source=Brondsema&sink=Goforth&subject=default">sample: Brondsema, Goforth, default</a><br>
		<a href="query?strategy=Prototype&source=Schamp&sink=Goforth&subject=default">sample: Schamp, Goforth, default</a><br>
		<a href="query?strategy=Default&source=EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70&sink=FB559CABDB811891B6D37E1439C06ED9D798EFD2&subject=java">sample: Dave, Frens, java (full fingerprints)</a><br>
		<a href="query?strategy=Prototype&source=8A335B856C4AE39A0C36A47F152C15A0F2454727&sink=FB559CABDB811891B6D37E1439C06ED9D798EFD2&subject=email">sample: Andy, Frens, email (full fingerprints)</a><br>
		<a href="query?strategy=Prototype&source=8A335B856C4AE39A0C36A47F152C15A0F2454727&sink=EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70&subject=cooking">sample: Andy, Dave, cooking (full fingerprints)</a><br>
		<h4>TrustServer commands</h4>
		<a href="command?cmd=start">Start server</a><br>
		<a href="command?cmd=stop">Stop server</a> NOTE: This will kill all python processes.<br>
		<a href="command?cmd=load1">Load data set 1</a><br>
		<a href="command?cmd=load2">Load data set 2</a><br>
		<h4>Web interface</h4>
		Or use <a href="form">this form</a><br>
		Or <a href="people">show people</a><br>
		<h4><a href="test">debug output</a></h4>""" +
		str(self.config) + 
		"""</body>
		</html>
		""")
		return apache.OK
	
	def people(self, req):
		try:
			sockobj = socket(AF_INET, SOCK_STREAM)
			sockobj.connect((self.config['trustserver']['host'], int(self.config['trustserver']['port'])))
			sockobj.send("people")
			result = ""
			#while 1:
			#	data = sockobj.recv(1024)
			#	if not data: break
			#	result += data 	
			# maybe deal with errors somewhere in here...
			#peops = pickle.loads(result)
			#for p in peops:
			#	print peops[p]
			#peopstr = string.join(peops, "\n")
			req.write("Result: %s\n\n" % (result))
		except error, (errno, errstr):
			req.write("Error(%s): %s" % (errno, errstr))
		return apache.OK  
	
	def command(self, req):
		if (req.method == "POST" or req.method == "GET"):
			form = util.FieldStorage(req, 1)
			cmd = form["cmd"]
			if (cmd == "start"):
				(stdin, stdout, stderr) = os.popen3("python /home/ams5/public_html/trustserver/TrustServer.py &")
				req.write("Did something.")
			elif (cmd == "stop"):
				(stdin, stdout, stderr) = os.popen3("kill -9 `pidof python`")
				req.write("Did something.")
			elif (cmd == "load1"):
				(stdin, stdout, stderr) = os.popen3("cd /home/ams5/public_html/trustserver && python load_rdf.py")
				req.write("std out: %s\n" % stdout.read())
				req.write("std err: %s\n" % stderr.read())
			elif (cmd == "load2"):
				(stdin, stdout, stderr) = os.popen3("cd /home/ams5/public_html/tests/small/ && python ../../trustserver/load_rdf.py")
				req.write("std out: %s\n" % stdout.read())
				req.write("std err: %s\n" % stderr.read())
			else:
				pass
			return apache.OK
		else:
			# hmm, something went horribly wrong.
			req.write("Error 41092.");
			return apache.OK
	
	def query(self, req):	
		if (req.method == "POST" or req.method == "GET"):
			form = util.FieldStorage(req, 1)
			strategy = form["strategy"]
			source = form["source"]
			sink = form["sink"]
			#subject = form["subject"]
			#req.write("Config: %s" % (self.config))
			
			if strategy == "": strategy = "Default"
				
			#handle the options here: 
			opt = {}
			opt["subject"] = form["subject"]
			
			options = "|".join(["%s=%s" % (k, v) for k, v in opt.items()])
			
			# first, check the PGP server:
			try:
				exec("from PGPPathfinders.%sPathfinder import %sPathfinder" % (self.config["pgpserver"]["pathfinder"],self.config["pgpserver"]["pathfinder"]))
				exec('pathfinder = %sPathfinder(self.config["%s"])' % (self.config["pgpserver"]["pathfinder"], self.config["pgpserver"]["pathfinder"]))
			except (ImportError):
				# put the hardcoded one here
				raise ImportError
			
			
			conn = pathfinder.connected(source, sink)
			graph = pathfinder.graph(source, sink)

			req.write("Graph: %s\nConnected: %s" % (graph, conn))
			
			# then, check the TrustServer:
			req.write("Source: %s\n Sink: %s\n Options: %s\n\n" % (source, sink, options))
			req.write("Host: %s\n Port: %i\n\n" % (self.config['trustserver']['host'], int(self.config['trustserver']['port'])))
			try:
				sockobj = socket(AF_INET, SOCK_STREAM)
				sockobj.connect((self.config['trustserver']['host'], int(self.config['trustserver']['port'])))
				sockobj.send("%s:%s:%s:%s" % (strategy, source, sink, options))
				result = ""
				while 1:
					data = sockobj.recv(1024)
					if not data: break
					result += data 	
				# maybe deal with errors somewhere in here...
				req.write("Result: %s\n\n" % (result))
			except error, (errno, errstr):
				req.write("Error(%s): %s" % (errno, errstr))
			return apache.OK    
				
		else:
			# hmm, something went horribly wrong.
			req.write("Error 41093.");
			return apache.OK
	
	def form(self, req):
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
		Strategy: <select name="strategy">""")
			
		files = [f for f in os.listdir(os.path.dirname(__file__)+'/../trustserver/TrustStrategies/') if re.compile("TPF.py$").search(f, 1)]
		for f in files:
			req.write("<option value=\"%s\">%s</option>\n" % (f[:-6], f[:-6]))
			
		req.write("""
		</select>
		<!--
		Action:<br/>
		<input type="radio" name="action" value="PGP"> PGP<br/>
		<input type="radio" name="action" value="trust"> Trust<br/>
		<input type="radio" name="action" value="both"> Both<br/>
		(note: this is a temporary thing, used for testing)-->
		<br/>
		<input type="submit" name="submit" value="Submit">
		</form>
		</body></html>""")
		return apache.OK
	
	#
	# test stuff; delete sometime
	#
	
	def test(self, req):
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

# takes a dictionary of all of the PythonOption directives from .htaccess
# and creates a multi-level dictionary
# (e.g., "PythonOption trustserver.host 127.0.0.1"
#	becomes
#	config["trustserver"]["host"] = "127.0.0.1")
# this is mainly used for loading the right options 
# for the right PGPPathfinder strategy
#
# just pass in req.get_options()

def parse_config(opts):
	config = {}
	for (k, v) in opts.items():
		t = config
		prev = config
		w = k.split('.')
		for i in w:
			try:
				t = t[i]
			except KeyError:
				t[i] = {}
				t = t[i]
			if w.index(i) == len(w) - 1:
				prev[i] = v
			prev = t
	return config
	

def handler(req):
	"""main handler; called by mod_python"""
	f = Frontend(req)
	return f.handle()
