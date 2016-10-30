from unittest import TestCase
import time

from tidle import TidleThread


class ThreadTestCase(TestCase):
    def test_thread(self):
        th = TidleThread(source='test')
        th.register('a')
        th.start()
        start = time.time()
        time.sleep(0.5)
        with th.work('a'):
            time.sleep(0.3)
        time.sleep(0.1)
        with th.work('a'):
            time.sleep(0.2)
        time.sleep(0.1)
        end = time.time()
        idle = th._calc_idle(th.metrics['a'], time.time())
        self.assertGreater(idle, 700)
        self.assertLess(idle, 800)
        self.assertGreater(end - start, 1.2)
        self.assertLess(end - start, 1.3)
