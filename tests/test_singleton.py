import re
from unittest import TestCase
import time

from tidle import MetricsSingleton, IdleMetrics, RssMetrics


A_PROG = re.compile(r'sample#a=(\d+)ms')
B_PROG = re.compile(r'sample#b=(\d+)ms')


class SingletonTestCase(TestCase):
    def test_all(self):
        s0 = MetricsSingleton(source='test')
        s1 = MetricsSingleton()
        s2 = MetricsSingleton()
        self.assertEqual(s0.thread, s1.thread)
        self.assertEqual(s0.thread, s2.thread)
        idles = [
            IdleMetrics(metrics=['a']),
            IdleMetrics(metrics=['a']),
            IdleMetrics(metrics=['b']),
        ]
        s0.register(idles[0])
        s1.register(idles[1])
        s2.register(idles[2])
        time.sleep(0.5)
        res0 = s0.format()
        res1 = s1.format()
        res2 = s2.format()
        val = int(A_PROG.search(res0).group(1))
        self.assertGreaterEqual(val, 1000)
        self.assertLess(val, 1020)
        val = int(B_PROG.search(res0).group(1))
        self.assertGreaterEqual(val, 500)
        self.assertLess(val, 510)
        val = int(A_PROG.search(res1).group(1))
        self.assertLess(val, 20)
        val = int(B_PROG.search(res1).group(1))
        self.assertLess(val, 10)
        val = int(A_PROG.search(res2).group(1))
        self.assertLess(val, 20)
        val = int(B_PROG.search(res2).group(1))
        self.assertLess(val, 10)
