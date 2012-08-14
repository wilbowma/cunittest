from unittest import TestSuite
import threading

class ConcurrentTestSuite(TestSuite):

  def __init__(self, threads=2, *args, **kwargs):
    self.threads = threads
    super(ConcurrentTestSuite, self).__init__(*args, **kwargs)

  def run(self, result, *args, **kwargs):
    pool = threading.BoundedSemaphore(self.threads)
    threads = []
    for test in self:
      def close():
        def _run():
          try:
            test(result, *args, **kwargs)
          finally:
            pool.release()
        return _run
      try:
        pool.acquire()
        thread = threading.Thread(target=close())
        threads.append(thread)
        thread.start()
      except:
        pool.release()
        raise
    for thread in threads:
      thread.join()
