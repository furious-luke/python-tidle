import threading
import time
from contextlib import contextmanager

import psutil

from .memory import get_memory_usage


class Metrics(object):
    def start(self):
        raise NotImplementedError

    def format(self):
        raise NotImplementedError


class RssMetrics(object):
    names = ['rss.max']

    def start(self):
        pass

    def capture(self):
        rss = get_memory_usage()
        return {
            'rss.max': (rss, 'kb')
        }

    def calculate(self):
        return self.capture()

    # def format(self):
    #     results = self.calculate()
    #     return ' '.join([
    #         'sample#{}={}kb'.format(n, results[n])
    #         for n in self.names
    #     ])


class DiffMetrics(Metrics):
    def __init__(self, metrics=[]):
        self.metrics = metrics
        self.data = [{}, {}]
        self.ss = 0
        self.ff = 1

    def start(self):
        for met in self.metrics:
            self.data[self.ss].update(met.capture())

    def capture(self):
        for met in self.metrics:
            self.data[self.ff].update(met.capture())
        self.ss = (self.ss + 1) & 1
        self.ff = (self.ff + 1) & 1

    def calculate(self):
        keys = self.data[self.ff].keys()
        results = {}
        for k in keys:
            ff = self.data[self.ff].get(k, (0.0, ''))
            ss = self.data[self.ss].get(k, (0.0, ''))
            value = (ff[0] - ss[0])
            results[k] = (value, ff[1] or ff[0])
        return results

    # def format(self):
    #     results = self.calc()
    #     return ' '.join([m.format(results) for m in self.metrics])


class CpuDiffMetrics(object):
    names = ['time.wall', 'time.cpu']

    def capture(self):
        return {
            'time.wall': (int(time.time() * 1000), 'ms'),
            'time.cpu': (int(time.clock() * 1000), 'ms')
        }

    def calculate(self):
        return self.capture()

    # def format(self, results):
    #     return ' '.join([
    #         'sample#{}={}ms'.format(n, int(results[n] * 1000))
    #         for n in self.names
    #     ])


class NetDiffMetrics(object):
    names = ['net.in', 'net.out']

    def capture(self):
        net = psutil.net_io_counters()
        return {
            'net.in': (int(net.bytes_recv / 1000), 'kb'),
            'net.out': (int(net.bytes_sent / 1000), 'kb')
        }

    def calculate(self):
        return self.capture()

    # def format(self, results):
    #     return ' '.join([
    #         'sample#{}={}kb'.format(n, int(results[n] / 1000))
    #         for n in self.names
    #     ])


class WorkMetrics(Metrics):
    def __init__(self, metrics=[]):
        self.metrics = metrics
        self.data = {}
        self._start = {}
        self._has_started = False
        self._lock = threading.Lock()

    def start(self):
        self._has_started = True
        for name in self.metrics:
            self.data[name] = 0.0

    @contextmanager
    def work(self, metric):
        if self._has_started:
            with self._lock:
                self._start[metric] = time.time()
            try:
                yield
            finally:
                with self._lock:
                    self.data.setdefault(metric, 0.0)
                    self.data[metric] += time.time() - self._start[metric]
                    self._start[metric] = None
        else:
            yield

    def calculate(self):
        with self._lock:
            cur_time = time.time()
            results = {}
            for met in self.metrics:
                results[met] = self.data.get(met, 0.0)
                start = self._start.get(met, None)
                if start is not None:
                    results[met] += cur_time - start
                    self._start[met] = cur_time
                self.data[met] = 0.0
                results[met] = (int(results[met] * 1000), 'ms')
        return results

    # def format(self):
    #     results = self.calc()
    #     return ' '.join([
    #         'sample#{}={}ms'.format(n, int(v * 1000))
    #         for n, v in results.items()
    #     ])


class IdleMetrics(WorkMetrics):
    def start(self):
        super().start()
        self.period_start = time.time()

    def calculate(self):
        results = super().calculate()
        cur_time = time.time()
        period = int((cur_time - self.period_start) * 1000)
        self.period_start = cur_time
        for n in results.keys():
            results[n] = (period - results[n][0], 'ms')
        return results
