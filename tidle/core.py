import time
import threading
from contextlib import contextmanager
from datetime import timedelta, datetime

import psutil


class Metrics(object):
    def __init__(self, logger=None, source=None):
        super().__init__()
        self.logger = logger if logger is not None else self
        self.source = 'source={} '.format(source) if source is not None else ''
        self.data = [{}, {}]
        self.work = {}
        self.start = 0
        self.finish = 1
        self._lock = threading.Lock()

    def capture(self, ii):
        raise NotImplemented

    def format(self, msg, results):
        return msg + ' '.join(['sample#{}={}'.format(k, v) for k, v in results.items()])

    def log(self):
        with self._lock:
            ss = self.start
            ff = self.finish
            self.start = (self.start + 1) & 1
            self.finish = (self.finish + 1) & 1
            self.capture(ff)
            results = dict([
                (k, self.data[ff][k] - self.data[ss][k])
                for k in self.data[ss].keys()
            ])
        msg = self.source
        self.logger.info(self.format(msg, results))

    def info(self, msg):
        print(msg)

    def _delay(self):
        now = datetime.now()
        delta = (now + timedelta(minutes=1)).replace(second=30, microsecond=0) - now
        return delta.total_seconds()

    def run(self):
        time.sleep(self._delay())
        self.capture(self.start)
        while 1:
            time.sleep(self._delay())
            self.log()


class CpuMetrics(Metrics):
    def capture(self, ii):
        self.data[ii]['time.wall'] = time.time()
        self.data[ii]['time.cpu'] = time.clock()

    def format(self, msg, results):
        return msg + ' '.join(['sample#{}={}ms'.format(k, int(v * 1000)) for k, v in results.items()])


class NetMetrics(Metrics):
    def capture(self, ii):
        net = psutil.net_io_counters()
        self.data[ii]['net.in'] = net.bytes_recv
        self.data[ii]['net.out'] = net.bytes_sent

    def format(self, msg, results):
        return msg + ' '.join(['sample#{}={}kb'.format(k, int(v / 1000)) for k, v in results.items()])


class WorkMetrics(Metrics):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work = {}

    @contextmanager
    def work(self, metric):
        with self._lock:
            self.work[metric] = time.time()
        try:
            yield
        finally:
            with self._lock:
                self.metrics[self.finish][metric] += (time.time() - self.work[metric]) * 1000
                self.work[metric] = None

    def capture(self, ii):
        cur_time = time.time()
        for met, start in self.work.items():
            if start is not None:
                self.metrics[ii][met] += (cur_time - start) * 1000
                self.work[met] = cur_time
        super().capture(ii)
