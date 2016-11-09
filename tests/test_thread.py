from unittest import TestCase
import time

from tidle import MetricsThread, IdleMetrics, RssMetrics


def do_work(met):
    for ii in range(10):
        with met.work('a'):
            time.sleep(0.3)


class IdleTestCase(TestCase):
    def test_basic(self):
        met = IdleMetrics(metrics=['a'])
        met.start()
        start = time.time()
        time.sleep(0.5)
        with met.work('a'):
            time.sleep(0.3)
        time.sleep(0.1)
        with met.work('a'):
            time.sleep(0.2)
        time.sleep(0.1)
        end = time.time()
        results = met.calculate()
        self.assertGreater(results['a'][0], 700)
        self.assertLess(results['a'][0], 800)
        self.assertGreater(end - start, 1.2)
        self.assertLess(end - start, 1.3)


class IdleAndMemoryTestCase(TestCase):
    def test_all(self):
        idles = [
            IdleMetrics(metrics=['a']),
            IdleMetrics(metrics=['a']),
            IdleMetrics(metrics=['b']),
            IdleMetrics(metrics=['b'])
        ]
        th = MetricsThread.launch(source='test', metrics=[
            idles[0],
            idles[1],
            idles[2],
            idles[3],
            RssMetrics()
        ])
        th._start()
        with idles[0].work('a'):
            time.sleep(0.3)
        time.sleep(0.1)
        with idles[0].work('a'):
            time.sleep(0.2)
        time.sleep(0.1)
