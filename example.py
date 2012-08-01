import cunittest
import threading

class Test(cunittest.ConcurrentTestCase):

  def run(self, result, lock=None, *args, **kwargs):
    self.assertNotEqual(lock, None)
    super(Test, self).run(result)

  def test_one(self):
    self.assertEqual(1,1)

  def test_two(self):
    self.assertEqual(2,1)

suite = cunittest.ConcurrentTestSuite()
suite.addTest(Test('test_one'))
suite.addTest(Test('test_two'))

cunittest.ConcurrentTextTestRunner(verbosity=2).run(suite,
    lock=threading.Lock())
