from unittest import TestCase
import time

from tidle import TidleThread


class WorkBoundaryTestCase(TestCase):
    def test_straddle(self):
        th = TidleThread(source='test')
        th.register('a')
        with th.work('a'):
            time.sleep(0.1)
            idle_0 = th._calc_idle(th.metrics['a'], time.time())
            time.sleep(0.2)
        idle_1 = th._calc_idle(th.metrics['a'], time.time())
        self.assertLess(idle_0, 10)
        self.assertLess(idle_1, 10)
