from .crunner import ConcurrentTestResult

class ConcurrentTestCase(TestCase):
  
  def defaultTestResult(self):
    return ConcurrentTestResult()
