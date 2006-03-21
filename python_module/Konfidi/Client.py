

class TrustClient:
    """A client for sending queries to the trustserver"""
    def __init__(self, config):
        self.config = config
        
    def Query(self, source, sink, subject):
        pass

	def send_query(self, strategy, options = "no_options=true"):
		sockobj = socket(AF_INET, SOCK_STREAM)
		sockobj.connect((self.config['host'], int(self.config['port'])))
		sockobj.send("%s:%s" % (strategy, options))
		result = ""
		while 1:
			data = sockobj.recv(1024)
			if not data: break
			result += data
		sockobj.close()
		return result