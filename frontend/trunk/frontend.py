# local
import dump
import xmlgen

# system
import os
import re
import sys
import traceback
import time
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
from xml.dom import minidom

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
		if (page == "query"):
			return self.query(self.req)
		if (page == "map"):
			return self.map(self.req)
		if (page == "form"):
			return self.form(self.req)
		if (page == "command"):
			return self.command(self.req)
		if (page == ""):
			return self.index(self.req)
		else:
			self.req.status = apache.HTTP_NOT_IMPLEMENTED
			self.req.content_type = "text/html"
			self.req.write("501: HTTP_NOT_IMPLEMENTED.  tried to access page=%s" % page)
			return apache.OK
			
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
		<br>Edge cases:<br>
		Ghandi, Spammer, email
		Ghandi, Scumbag, email
		<h4>TrustServer commands</h4>
		<a href="command?cmd=start">Start server</a><br>
		<a href="command?cmd=stop">Stop server</a> <!--NOTE: This will kill all python processes.--><br>
		<a href="command?cmd=load1">Load data set 1 (schamp, laing, brondsema)</a><br>
		<a href="command?cmd=load2">Load data set 2 (real keys, etc)</a><br>
		<a href="command?cmd=load3">Load data set 3 (edge cases)</a><br>
		<h4>Web interface</h4>
		Or use <a href="form">this form</a><br>
		Or <a href="query?strategy=PeopleDump&source=foo&sink=bar&subject=baz&pgpquery=0">show people</a><br/>
		Or <a href="map">Map all trust relationships and inferences</a><br/>
		<h4><a href="test">debug output</a></h4>""" +
		str(self.config) + 
		"""</body>
		</html>
		""")
		return apache.OK
	
	def command(self, req):
		if (req.method == "POST" or req.method == "GET"):
			form = util.FieldStorage(req, 1)
			cmd = form["cmd"]
			if (cmd == "start"):
				(stdin, stdout, stderr) = os.popen3("/home/ams5/public_html/trustserver/trustserver.sh start")
				#req.write("std out: %s\n" % stdout.read())
				#req.write("std err: %s\n" % stderr.read())
				req.write("Did something.")
			elif (cmd == "stop"):
				(stdin, stdout, stderr) = os.popen3("kill -9 1456 1459 ")
				#(stdin, stdout, stderr) = os.popen3("kill -9 `pidof python`")
				#(stdin, stdout, stderr) = os.popen3("/home/ams5/public_html/trustserver/trustserver.sh stop")
				#req.write("std out: %s\n" % stdout.read())
				#req.write("std err: %s\n" % stderr.read())
				req.write("Did something.")
			elif (cmd == "load1"):
				(stdin, stdout, stderr) = os.popen3("cd /home/ams5/public_html/tests/prototype && svn cat http://brondsema.gotdns.com/svn/dmail/clients/simple/load_rdf.py | python")
				req.write("std out: %s\n" % stdout.read())
				req.write("std err: %s\n" % stderr.read())
			elif (cmd == "load2"):
				(stdin, stdout, stderr) = os.popen3("cd /home/ams5/public_html/tests/small/ && svn cat http://brondsema.gotdns.com/svn/dmail/clients/simple/load_rdf.py | python")
				req.write("std out: %s\n" % stdout.read())
				req.write("std err: %s\n" % stderr.read())
			elif (cmd == "load3"):
				(stdin, stdout, stderr) = os.popen3("cd /home/ams5/public_html/tests/edgecases/ && svn cat http://brondsema.gotdns.com/svn/dmail/clients/simple/load_rdf.py | python")
				req.write("stdout: %s\n" % stdout.read())
				req.write("stderr: %s\n" % stderr.read())
			else:

				pass
			return apache.OK
		else:
			# hmm, something went horribly wrong.
			req.status = apache.HTTP_METHOD_NOT_ALLOWED
			req.content_type = "text/html"
			req.write("405: HTTP_METHOD_NOT_ALLOWED: %s" % req.method)
			return apache.OK
	
	def query(self, req):	
		if (req.method == "POST" or req.method == "GET"):
			form = util.FieldStorage(req, 1)
			try:
				strategy = form["strategy"]
			except KeyError:
				strategy = self.config["trustserver"]["strategy"]
				
			source = form["source"]
			sink = form["sink"]

		
			opt = self.parse_options(form)
			options = self.parse_options(form, True)
			
			pgpresult = None
			if self.config["debug"] == "1":
				reload(xmlgen)
			f = xmlgen.Factory()
			r = []
			if opt["pgpquery"]:
				# first, check the PGP server:
				try:
					exec("from PGPPathfinders.%sPathfinder import %sPathfinder" % (self.config["pgpserver"]["pathfinder"],self.config["pgpserver"]["pathfinder"]))
					exec('pathfinder = %sPathfinder(self.config["%s"])' % (self.config["pgpserver"]["pathfinder"], self.config["pgpserver"]["pathfinder"]))
				except (ImportError):
					# put the hardcoded one here
					raise ImportError
				pgptime = time.time()
				pgp_result = str(pathfinder.graph(source, sink))
				pgptime = time.time() - pgptime
				
				pgp_result = minidom.parseString(pgp_result).documentElement
				connected = pgp_result.getElementsByTagName("connected")[0]
				pgp_path = pgp_result.getElementsByTagName("path")[0]
				pgp_error = pgp_result.getElementsByTagName("error")[0]
				
				pgp_result = f.pgp_result(search_time=pgptime)[connected.toxml(), pgp_path.toxml(), pgp_error.toxml()]
				
			
			if opt["trustquery"]:
				# then, check the TrustServer:
				try:
					trustresult = self.send_query(strategy, source, sink, options)
					trustresult = minidom.parseString(trustresult).documentElement
					try:
						trust_rating = trustresult.getElementsByTagName("rating")[0].toxml()
					except IndexError:
						trust_rating = str(f.rating("0"))
					try:
						trust_path = trustresult.getElementsByTagName("path")[0].toxml()
					except IndexError:
						trust_path = str(f.path("N/A"))
					try:
						trust_data = trustresult.getElementsByTagName("data")[0].toxml()
					except IndexError:
						trust_data = str(f.data("N/A"))
					try:
						trust_error = trustresult.getElementsByTagName("error")[0].toxml()
					except IndexError:
						trust_error = str(f.error("None"))
					
					trust_result = f.trust_result(trust_host = self.config['trustserver']['host'], trust_port = self.config['trustserver']['port'])[trust_rating, trust_path, trust_data, trust_error]
				except error, (errno, errstr):
					req.write("Error(%s): %s" % (errno, errstr))
			
			if opt["trustoutput"] == "short":
				if opt["pgpquery"] and connected.firstChild.nodeValue == "0":
					req.write("-1")
				else:
					#trust_rating = minidom.parseString(trustresult).documentElement
					#print trust_rating
					req.write(trustresult.getElementsByTagName("rating")[0].firstChild.nodeValue)
			else:
				r.extend([f.source(source), f.sink(sink), f.options(options)])
				if opt["pgpquery"]:
					r.append(pgp_result)
				if opt["trustquery"]:
					r.append(trust_result)
				req.write(self.xml_indenter(str(f.result[r])))
			return apache.OK
			
				
		else:
			# hmm, something went horribly wrong.
			req.status = apache.HTTP_METHOD_NOT_ALLOWED
			req.content_type = "text/html"
			req.write("405: HTTP_METHOD_NOT_ALLOWED: %s" % req.method)
			return apache.OK
	
	def xml_indenter(self, xml, indent=0):
		if len(xml) == 0:
			#print "None\n"
			return "";
		(tag, xml) = self.munch_tag(xml)
		if tag[0] != '<' or tag[-2:] == '/>' or tag[-3:] == '/ >':
			return "%s%s\n%s" % ("\t"*indent, tag, self.xml_indenter(xml, indent))
		elif tag[:2] == '</':
			return "%s%s\n%s" % ("\t"*(indent-1), tag, self.xml_indenter(xml, indent-1))
		else:
			return "%s%s\n%s" % ("\t"*indent, tag, self.xml_indenter(xml, indent+1))
		
	def munch_tag(self, xml):
		if xml[0] != '<':
			bound = xml.index('<')
			literal = xml[:bound]
			xml = xml[bound:]
			return (literal, xml)
		
		bound = xml.index('>') + 1
		tag = xml[:bound]
		xml = xml[bound:]
		return (tag, xml)
			
	def send_query(self, strategy, source="foo", sink="bar", options="baz"):
		sockobj = socket(AF_INET, SOCK_STREAM)
		sockobj.connect((self.config['trustserver']['host'], int(self.config['trustserver']['port'])))
		sockobj.send("%s:%s:%s:%s" % (strategy, source, sink, options))
		result = ""
		while 1:
			data = sockobj.recv(1024)
			if not data: break
			result += data
		#sockobj.close()
		return result
	
	def parse_options(self, form, retstr = False):
		#handle the options here: 
		opt = {}
		try:
			opt["pgpquery"] = int(form["pgpquery"])
		except KeyError:
			opt["pgpquery"] = int(self.config["pgpserver"]["query"])
		try:
			opt["trustquery"] = int(form["trustquery"])
		except KeyError:
			opt["trustquery"] = int(self.config["trustserver"]["query"])
		try:
			opt["trustoutput"] = form["trustoutput"]
		except KeyError:
			opt["trustoutput"] = self.config["trustserver"]["output"]
		try:
			opt["pgpoutput"] = form["pgpoutput"]
		except KeyError:
			opt["pgpoutput"] = self.config["pgpserver"]["output"]
		try:
			opt["subject"] = form["subject"]
		except KeyError:
			opt["subject"] = "default"
		try:
			opt["map_errors"] = form["map_errors"]
		except KeyError:
			opt["map_errors"] = 0
			
		if retstr:
			return "|".join(["%s=%s" % (k, v) for k, v in opt.items()])	
		else:
			return opt
		
	def map(self, req):
		form = util.FieldStorage(req, 1)
		strategy = form["strategy"]
		options = self.parse_options(form,True)
		opts = self.parse_options(form)
		req.content_type = "text/html"
		peops = self.send_query("PeopleList")
		peops = minidom.parseString(peops).documentElement.getElementsByTagName("data")[0].firstChild.nodeValue.split('|')
		peops[0] = string.strip(peops[0])
		#req.write( "foo\n" )
		req.write( "%s\n" % peops )
		req.write( "%s\n" % options )
		req.write("<table border=1><tr><td>Source:</td><td>Sink:</td><td>Query Time:</td><td>Lock Time:</td><td>Result:</td></tr>\n")
		for source in peops:
			for sink in peops:
				if source == sink: continue
				r = self.send_query(strategy, source, sink, options)
				rating = float(minidom.parseString(r).documentElement.getElementsByTagName("rating")[0].firstChild.nodeValue)
				if rating >= 0 and opts["map_errors"] != 1:
					req.write( "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (source, sink, r) )
		
		req.write("</table>\n")
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
		Sink: <input type="text" name="sink"><br/><br/>
		Subject: <input type="text" name="subject"><br/>
		Strategy: <select name="strategy">""")
			
		files = [f for f in os.listdir(os.path.dirname(__file__)+'/../../trustserver/trunk/TrustStrategies/') if re.compile("TPF.py$").search(f, 1)]
		for f in files:
			req.write("<option value=\"%s\">%s</option>\n" % (f[:-6], f[:-6]))
			
		req.write("""
		</select><br/><br/>
		Query:<br/>
		PGP Server:<br/>
		Yes: <input type="radio" name="pgpquery" value="1">  No: <input type="radio" name="pgpquery" value="0"><br/>
		Trustserver: <br/>
		Yes: <input type="radio" name="trustquery" value="1">  No: <input type="radio" name="trustquery" value="0"><br/><br/>
		
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
		req.write("sys.path: %s\n" % sys.path)
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
	apache.log_error("uri ams5 1: %s" % uri, apache.APLOG_NOTICE)
	try:
		uri += req.subprocess_env['PATH_INFO']
		apache.log_error("uri ams5 2: %s" % uri, apache.APLOG_NOTICE)
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
	from frontend import Frontend
	f = Frontend(req)
	return f.handle()
