import dump
from mod_python import apache

import os
#import sys

def handler(req):
    req.allow_methods(["GET", "PUT"])
    apache.log_error("request!", apache.APLOG_NOTICE)
    
    if req.get_config().has_key('PythonDebug'):
        reload(dump)
    
    if (req.parsed_uri[apache.URI_PATH] == "/~dpb2/foafserver/test"):
        return test(req)
    elif (req.method == "GET"):
        return get(req)
    elif (req.method == "PUT"):
        return put(req)
    else:
        return apache.HTTP_NOT_IMPLEMENTED

def get(req):
    req.write(dump.dump(req.parsed_uri))
    return apache.OK

def test(req):
    req.content_type = "text/plain"
    req.write(dump.dump(req.parsed_uri))
    #req.write(dump.dump(req))
    req.write(dump.dump(req.get_options()))
    req.write(dump.dump(req.get_config()))
    
    req.write("server_root=" + apache.server_root() + "<br>")
    if apache.mpm_query(apache.AP_MPMQ_IS_THREADED):
        req.write("mpm is threaded<br>")
    else:
        req.write("mpm is NOT threaded<br>")
    if apache.mpm_query(apache.AP_MPMQ_IS_FORKED):
        req.write("mpm is forked<br>")
    else:
        req.write("mpm is NOT forked<br>")
    
    
    return apache.OK
