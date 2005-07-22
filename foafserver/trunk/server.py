#  Copyright (C) 2005-2005 Dave Brondsema, Andrew Schamp
#  This file is part of Konfidi http://konfidi.org/
#  It is licensed under two alternative licenses (your choice):
#      1. Apache License, Version 2.0
#      2. GNU Lesser General Public License, Version 2.1
#
#
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from mod_python import apache

# local
import dump
from SignedFOAF import SignedFOAF
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

def is_secure(req):
    req.add_common_vars()
    try:
        return req.subprocess_env["HTTPS"] == "on"
    except KeyError:
        return False

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
    req.allow_methods(["GET", "PUT", "DELETE"])
    
    if req.get_config().has_key('PythonDebug'):
        reload(dump)
    
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
    elif (req.method == "DELETE"):
        return delete(req)
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
    
    <h3>Retrieving</h3>
    Do an HTTP GET using a URL of the PGP fingerprint.  Examples:
    <br>
    <a href="8A335B856C4AE39A0C36A47F152C15A0F2454727">andy schamp</a><br>
    <a href="EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70">dave brondsema</a><br>
    <br>
    Different outputs will be served when the request has an HTTP 'Accept:' header with a value in the following: "multipart/signed", "application/pgp-signature", {"application/xml+rdf", "text/xml", "text/*", "application/xml"}
    
    <h3>Uploading</h3>
    <b>Human web interface:</b> Use this <a href="form">web form</a><br>
    <b>Programmatic interface:</b> Do an HTTP PUT using a URI of the PGP fingerprint (like retrieving).  You must send a Content-Type: multipart/signed message that contains the FOAF document and the pgp-signature.
    
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
            foaf = FOAFDoc()
            foaf.load(req.get_options()['storage.dir.rdf'], uri)
            sig = PGPSig()
            sig.load(req.get_options()['storage.dir.sig'], uri)
            
            signedFOAF = SignedFOAF(foaf, sig, req.subprocess_env['HTTP_ACCEPT'])
            
            req.content_type = signedFOAF.content_type()
            req.write(signedFOAF.body())
            return apache.OK
        except IOError:
            apache.log_error("not found: requested " + uri, apache.APLOG_ERR)
            return apache.HTTP_NOT_FOUND
    else:
        apache.log_error("invalid: requested " + uri, apache.APLOG_ERR)
        return apache.HTTP_FORBIDDEN

def put(req):
    fingerprint = uniqueURI(req)
    # security check, allow hex only
    if ishex(uri):
        # Content-Type: must begin with multipart/signed
        if "Content-Type:" in req.headers_in and req.headers_in["Content-Type:"].find("multipart/signed") == 0:
            content = req.read()
            foaf = FOAFDoc(content)
            sig = PGPSig()
            signedFOAF = SignedFOAF(foaf, sig)
            signedFOAF.verify_sig()
            err = storefoaf(req, signedFOAF, fingerprint)
        else:
            err = "Must PUT with Content-Type: multipart/signed"
        
        if err:
            apache.log_error(err, apache.APLOG_NOTICE)
            req.status = apache.HTTP_NOT_ACCEPTABLE
            req.write("Error: " + err)
            return apache.OK
        else:
            #TODO: if a new file, return 201 (Created)
            return apache.OK
    else:
        apache.log_error("invalid: requested " + uri, apache.APLOG_ERR)
        return apache.HTTP_FORBIDDEN

def delete(req):
    fingerprint = uniqueURI(req)
    # security check, allow hex only
    if ishex(uri):
        return apache.HTTP_NOT_IMPLEMENTED
    else:
        apache.log_error("invalid: requested " + uri, apache.APLOG_ERR)
        return apache.HTTP_FORBIDDEN

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
        
        inputs_exist = True
        if 'submit_upload' in form:
            if not(form["foaf_file"].filename):
                req.write("<p>You must select a FOAF file to upload</p>")
                inputs_exist = False
            if not(form["sig_file"].filename):
                req.write("<p>You must select a PGP signature file to upload</p>")
                inputs_exist = False
            foaf_content = form["foaf_file"].value
            sig_content = form["sig_file"].value
        else:
            foaf_content = form["foaf_content"]
            sig_content = form["sig_content"]
            if len(foaf_content) == 0:
                req.write("<p>You must enter a FOAF document</p>")
                inputs_exist = False
            if len(sig_content) == 0:
                req.write("<p>You must enter a PGP signature</p>")
                inputs_exist = False
        
        if inputs_exist:
            foaf = FOAFDoc(foaf_content)
            sig = PGPSig(sig_content)
            signedFOAF = SignedFOAF(foaf, sig)
            signedFOAF.verify_sig()
            store_error = storefoaf(req, signedFOAF)
            if store_error:
                req.write("<p>Error: " + store_error + "</p>")
            else:
                req.write("<p>FOAF succesfully uploaded</p>")
    
    # TODO: -----BEGIN PGP SIGNED MESSAGE----- option
    req.write("""
    <h2>Submit an signed FOAF record</h2>
    <form action="form" method="POST" enctype="multipart/form-data">
    Upload FOAF file: <input type="file" name="foaf_file"/><br/>
    Upload PGP signature file: <input type="file" name="sig_file"/><br/>
    <input type="submit" name="submit_upload" value="Submit">
    </form>
    <br/><hr/><br/>
    Or,<br/>
    <form action="form" method="POST">
    paste FOAF XML:<br/>
    <textarea name="foaf_content" rows="12" cols="50" wrap="none"></textarea><br/>
    paste PGP signature:<br/>
    <textarea name="sig_content" rows="8" cols="50" wrap="none"></textarea><br/>
    <input type="submit" name="submit_text" value="Submit">
    </form>
    </body></html>""")
    return apache.OK

#
# workhorse utilities
#


def storefoaf(req, signedFOAF, uri_fingerprint=""):
    try:
        fingerprint = signedFOAF.foaf.validate(uri_fingerprint, req.get_options()['validate.wot'] == "1")
    except FOAFServerError:
        return str(sys.exc_info()[1])
    # TODO: get fingerprint from signedFOAF.signature and compare that to fingeprint
    signedFOAF.signature.save(req.get_options()['storage.dir.sig'], fingerprint)
    filename = signedFOAF.foaf.save(req.get_options()['storage.dir.rdf'], fingerprint)
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
    req.write("\nRequest headers:\n-------------\n")
    req.write(dump.dump(req.headers_in))
    
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
