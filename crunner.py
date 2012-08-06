import threading 
from cStringIO import StringIO
from unittest import TextTestRunner
try:
  from unittest import TextTestResult
except ImportError:
  from unittest import _TextTestResult as TextTestResult
try:
  from unittest import registerResult
except ImportError:
  def registerResult(*args, **kwargs):
    pass
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

class ConcurrentTextTestResult(TextTestResult):

  def __init__(self, *args, **kwargs):
    super(ConcurrentTextTestResult, self).__init__(*args, **kwargs)
    self.sstreams = []

  def _wrap_method(self, f, test, *args, **kwargs):
    stream = self.stream 
    if not hasattr(test, "result_stream"):
      test.result_stream = _WritelnDecorator(StringIO())
      self.sstreams.append(test.result_stream)
    self.stream = test.result_stream
    res = getattr(super(ConcurrentTextTestResult, self), f)(test, *args,
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

class ConcurrentTextTestRunner(TextTestRunner):
  resultclass = ConcurrentTextTestResult

  def run(self, test, *args, **kwargs):
    "Run the given test case or test suite."
    result = self._makeResult()
    registerResult(result)
# These don't exist in 2.6
    try:
      result.failfast = self.failfast
      result.buffer = self.buffer
    except:
      pass
    startTime = time.time()
    startTestRun = getattr(result, 'startTestRun', None)
    if startTestRun is not None:
      startTestRun()
    try:
      test(result, *args, **kwargs)
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
