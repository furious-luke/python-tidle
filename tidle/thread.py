import time
from datetime import timedelta, datetime
from contextlib import contextmanager
import threading


class TidleThread(threading.Thread):
    def __init__(self, logger=None, source=None):
        super().__init__()
        self.source = ('source=' + source) if source else ''
        self.logger = logger if logger is not None else self
        self.daemon = True
        self.metrics = {}

    def info(self, msg):
        print(msg)

    def register(self, metric):
        self.metrics[metric] = {
            'idle_start': time.time(),
            'work_start': None,
            'work': 0,
        }

    @contextmanager
    def work(self, metric):
        tg = self.metrics[metric]
        tg['work_start'] = time.time()
        try:
            yield
        finally:
            self.metrics[metric]['work'] += (time.time() - tg['work_start']) * 1000
            tg['work_start'] = None

    def _calc_idle(self, tg, cur_time):
        if tg['work_start'] is not None:
            tg['work'] += (cur_time - tg['work_start']) * 1000
            tg['work_start'] = cur_time
        idle = (cur_time - tg['idle_start']) * 1000 - tg['work']
        tg['idle_start'] = cur_time
        tg['work'] = 0
        return idle

    def _delay(self):
        now = datetime.now()
        delta = (now + timedelta(minutes=1)).replace(second=30, microsecond=0) - now
        return delta.total_seconds()

    def run(self):
        while 1:
            time.sleep(self._delay())
            msg = self.source
            cur = time.time()
            for metric, tg in self.metrics.items():
                idle = self._calc_idle(tg, cur)
                msg += ' sample#%s=%d' % (metric, idle)
            self.logger.info(msg)
