import time
from datetime import timedelta, datetime
import threading

from .utils import Borg


class MetricsThread(threading.Thread):
    @classmethod
    def launch(cls, *args, **kwargs):
        th = cls(*args, **kwargs)
        th.daemon = True
        th.start()
        return th

    def __init__(self, logger=None, source=None, metrics=[]):
        super().__init__()
        self.logger = logger if logger is not None else self
        self.source = 'source={} '.format(source) if source is not None else ''
        self.metrics = metrics
        self._has_started = False
        self._lock = threading.Lock()

    def register(self, metric):
        with self._lock:
            self.metrics.append(metric)
            if self._has_started:
                metric.start()

    def calculate(self):
        with self._lock:
            results = {}
            for met in self.metrics:
                cur_res = met.calculate()
                for k, v in cur_res.items():
                    if k not in results:
                        results[k] = v
                    else:
                        assert results[k][1] == v[1], 'mismatched units'
                        results[k] = (results[k][0] + v[0], v[1])
            return results

    def format(self):
        results = self.calculate()
        msg = self.source + ' '.join(
            ['measure#{}={}{}'.format(k, v[0], v[1])
             for k, v in results.items()]
        )
        return msg

    def log(self):
        self.logger.info(self.format())

    def info(self, msg):
        print(msg)

    def _delay(self):
        now = datetime.now()
        delta = (
            (now + timedelta(minutes=1)).replace(second=30, microsecond=0) -
            now
        )
        return delta.total_seconds()

    def _start(self):  # Dammit.
        with self._lock:
            for met in self.metrics:
                met.start()
            self._has_started = True

    def run(self):
        time.sleep(self._delay())
        self._start()
        while 1:
            time.sleep(self._delay())
            self.log()


class MetricsSingleton(Borg):
    _lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        super().__init__()
        with self._lock:
            th = getattr(self, 'thread', None)
            if th is None:
                setattr(self, 'thread', MetricsThread.launch(*args, **kwargs))
            else:
                # TODO: Check other values for consitency.
                for met in kwargs.get('metrics', []):
                    th.register(met)

    def __getattr__(self, name):
        try:
            th = self.__dict__['thread']
        except KeyError:
            raise AttributeError
        return getattr(th, name)
