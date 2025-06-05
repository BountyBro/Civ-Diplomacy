''' Testing Framework: Python unittest module.
How to use:
- Write tests as methods inside the 'Tests' class below.
    - All methods must use self as the only argument.
    - All methods must use an assert method, which can be found under ut.TestCase.assert and then autofilling the remaining portion of the assert method.
    - All methods must not start with _.
    - Errors handling is done using the following line: with self.assertRaises(ErrorName):
- Run this file as main.
'''
##### DEPENDENCIES #####
from civ import Civ
from model import Model
from planet import Planet
import unittest as ut   # Testing framework module.



##### CLASSES ####
class Tests(ut.TestCase):
    def sample_true_test(self):
        self.assertTrue(True)

    def sample_false_test(self):
            self.assertTrue(False)



##### MAIN #####
if __name__ == "__main__":
    test_functions = [fn for fn in dir(Tests) if (not fn in [pFn for pFn in dir(ut.TestCase)]) and (not fn.startswith("_")) and callable(getattr(Tests(), fn))]
    ut.runner.TextTestRunner().run(ut.TestLoader().loadTestsFromNames([f"civTests.Tests.{fn}" for fn in test_functions]))