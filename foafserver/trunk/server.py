import dump
from mod_python import apache

import os

# initialization code
phase = 'init'

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
    apache.log_error("request!", apache.APLOG_NOTICE)
    
    if req.get_config().has_key('PythonDebug'):
        reload(dump)
    
    if (uniqueURI(req) == "test"):
        return test(req)
    elif (req.method == "GET"):
        return get(req)
    elif (req.method == "PUT"):
        return put(req)
    else:
        return apache.HTTP_NOT_IMPLEMENTED

def get(req):
    req.write(uniqueURI(req))
    return apache.OK

def test(req):
    req.content_type = "text/plain"
    """
    if phase == 'init':
        init_var2 = 2
        var3 = 1
        phase = 'request'
    var3 += 1
    req.write("\n" + dump.dump(init_var) + dump.dump(init_var2) + dump.dump(var3))
    """
    
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
        
    #req.write(dump.dump(apache.config_tree()))
    
    
    return apache.OK
