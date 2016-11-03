import threading

from .core import CpuMetric, NetMetric


class MetricsThread(threading.Thread):
    @classmethod
    def launch(cls, *args, **kwargs):
        th = cls(*args, **kwargs)
        th.daemon = True
        th.start()


class CpuThread(CpuMetrics, MetricsThread):
    pass


class NetThread(NetMetrics, MetricsThread):
    pass
