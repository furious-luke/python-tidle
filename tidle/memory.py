import resource
import logging


metrics = logging.getLogger('metrics')


def get_memory_usage():
    """ Returns the current memory usage in KBs.
    """
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


class MemoryMetrics(object):
    def __init__(self, tmpl='measure#memory-increase=%dmb'):
        self.tmpl = tmpl

    def __enter__(self):
        self.start = get_memory_usage()
        return self

    def __exit__(self, *args):
        self.end = get_memory_usage()
        self.usage = self.end - self.start
        metrics.info(self.tmpl % self.usage)
