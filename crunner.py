import threading 
from cStringIO import StringIO
from unittest import TextTestRunner
from unittest import registerResult
import time

# For some reason I can't import this, so I've inlined it
class _WritelnDecorator:
  """Used to decorate file-like objects with a handy 'writeln' method"""

  def __init__(self,stream):
    self.stream = stream

  def __getattr__(self, attr):
    return getattr(self.stream,attr)

  def writeln(self, arg=None):
    if arg: self.write(arg) 
    self.write('\n') 

class ConcurrentTestResult(TextTestResult):

  def __init__(self, *args, **kwargs):
    super(ConcurrentTestResult, self).__init__(*args, **kwargs)
    self.sstreams = []

  def _wrap_method(self, f, test, *args, **kwargs):
    stream = self.stream 
    if not hasattr(test, "result_stream"):
      test.result_stream = _WritelnDecorator(StringIO())
      self.sstreams.append(test.result_stream)
    self.stream = test.result_stream
    res = getattr(super(ConcurrentTestResult, self), f)(test, *args,
        **kwargs)
    self.stream = stream
    return res

  def startTest(self, test, *args, **kwargs):
    return self._wrap_method("startTest", test, *args, **kwargs)

  def addSuccess(self, test, *args, **kwargs):
    return self._wrap_method("addSuccess", test, *args, **kwargs)

  def addError(self, test, *args, **kwargs):
    return self._wrap_method("addError", test, *args, **kwargs)

  def addFailure(self, test, *args, **kwargs):
    return self._wrap_method("addFailure", test, *args, **kwargs)

  def addSkip(self, test, *args, **kwargs):
    return self._wrap_method("addSkip", test, *args, **kwargs)

  def addExpectedFailure(self, test, *args, **kwargs):
    return self._wrap_method("addExpectedFailure", test, *args, **kwargs)

  def addUnexpectedSuccess(self, test, *args, **kwargs):
    return self._wrap_method("addUnexpectedSuccess", test, *args, **kwargs)

  def printErrors(self):
    self.printErrorList('ERROR', self.errors, True)
    self.printErrorList('FAIL', self.failures, False)

  def printErrorList(self, flavour, errors, flag):
    tests = []
    for test, err in errors:
      stream = test.result_stream
      if flag and test not in tests:
        stream.writeln()
        tests.append(test)
      stream.writeln(self.separator1)
      stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
      stream.writeln(self.separator2)
      stream.writeln("%s" % err)

class ConcurrentTestRunner(TextTestRunner):
  resultclass = ConcurrentTestResult

  def run(self, test, threads=2):
    "Run the given test case or test suite."
    result = self._makeResult()
    registerResult(result)
    result.failfast = self.failfast
    result.buffer = self.buffer
    startTime = time.time()
    startTestRun = getattr(result, 'startTestRun', None)
    if startTestRun is not None:
      startTestRun()
    locks = [threading.Lock() for i in range(3)]
    assert len(locks) == 3, "Incorrect number of locks"
    pool = threading.BoundedSemaphore(threads)
    rlocks = [threading.RLock() for _ in test]
    suite = [(test,lock) for (test,lock) in zip(test,rlocks)]
    def _run(lock, test):
      try:
        lock.acquire()
        test.locks = locks
        test(result)
      except:
        raise
      finally:
        pool.release()
        lock.release()
    try:
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
    finally:
      stopTestRun = getattr(result, 'stopTestRun', None)
      if stopTestRun is not None:
        stopTestRun()
    stopTime = time.time()
    timeTaken = stopTime - startTime
    result.printErrors()
    for stream in result.sstreams:
      self.stream.write(stream.getvalue())
      self.stream.flush()

    if hasattr(result, 'separator2'):
      self.stream.writeln(result.separator2)
    run = result.testsRun
    self.stream.writeln("Ran %d test%s in %.3fs" %
                        (run, run != 1 and "s" or "", timeTaken))
    self.stream.writeln()

    expectedFails = unexpectedSuccesses = skipped = 0
    try:
      results = map(len, (result.expectedFailures,
                          result.unexpectedSuccesses,
                          result.skipped))
    except AttributeError:
      pass
    else:
      expectedFails, unexpectedSuccesses, skipped = results

    infos = []
    if not result.wasSuccessful():
      self.stream.write("FAILED")
      failed, errored = map(len, (result.failures, result.errors))
      if failed:
        infos.append("failures=%d" % failed)
      if errored:
        infos.append("errors=%d" % errored)
    else:
      self.stream.write("OK")
    if skipped:
      infos.append("skipped=%d" % skipped)
    if expectedFails:
      infos.append("expected failures=%d" % expectedFails)
    if unexpectedSuccesses:
      infos.append("unexpected successes=%d" % unexpectedSuccesses)
    if infos:
      self.stream.writeln(" (%s)" % (", ".join(infos),))
    else:
      self.stream.write("\n")
    return result
