class PGPPathfinder:
    def __init__(self, config):
        self.config = config

    def graph(self, source, sink, limit):
        raise NotImplementedError

    def connected(self, source, sink, limit):
        raise NotImplementedError

