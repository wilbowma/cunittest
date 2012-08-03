from unittest import TestSuite
import threading

class ConcurrentTestSuite(TestSuite):

  def __init__(self, threads=2, *args, **kwargs):
    self.threads = threads
    super(ConcurrentTestSuite, self).__init__(*args, **kwargs)

  def run(self, result, *args, **kwargs):
    pool = threading.BoundedSemaphore(self.threads)
    rlocks = [threading.RLock() for _ in self]
    suite = [(test,lock) for (test,lock) in zip(self,rlocks)]
    def _run(lock, test):
      try:
#        lock.acquire()
        test(result, *args, **kwargs)
      except:
        raise
      finally:
        pool.release()
#        lock.release()
    threads = []
    for (test,lock) in suite:
      try:
        pool.acquire()
        thread = threading.Thread(target=_run, args=[lock, test])
        threads.append(thread)
        thread.start()
      except:
        raise
    for thread in threads:
      thread.join()
