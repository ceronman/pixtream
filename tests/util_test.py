import sys
sys.path.append('..')

import unittest
import util

class ExceptionDecoratorTest(unittest.TestCase):
    def test_functionwrapps(self):

        @util.handle_exception(ZeroDivisionError, None)
        def divide_function(a, b):
            return a / b

        self.assertEqual(5, divide_function(10, 2))
        self.assertRaises(ZeroDivisionError, divide_function, 10, 0)

    def test_attributeerror(self):
        fail = True

        def handler(e):
            fail = False

        @util.handle_exception(AttributeError, handler)
        def test_function():
            return 'hello'.some_attribute

        self.assert_(fail)

    def test_nonehandler(self):

        @util.handle_exception(AttributeError, None)
        def test_function():
            return 'hello'.some_attribute

        self.assertRaises(AttributeError, test_function)

    def test_noneexception(self):

        @util.handle_exception(None, None)
        def test_function():
            return 'hello'.some_attribute

        self.assertRaises(Exception, test_function)

if __name__ == '__main__':
    unittest.main()
