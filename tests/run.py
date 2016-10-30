import random
import time

from tidle import TidleThread


if __name__ == '__main__':
        th = TidleThread(source='test')
        th.register('a')
        th.start()
        while 1:
            time.sleep(10)
            with th.work('a'):
                cur = time.time()
                while time.time() - cur < 10:
                    r = random.randint(0, 1000)
