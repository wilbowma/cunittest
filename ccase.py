from .crunner import ConcurrentTextTestResult
from unittest import TestCase

class ConcurrentTestCase(TestCase):
  
  def defaultTestResult(self):
    return ConcurrentTextTestResult()
