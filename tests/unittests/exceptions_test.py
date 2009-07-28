import unittest
from pixtream.util.exceptions import handle_exception

class ExceptionDecoratorTest(unittest.TestCase):
    def test_functionwrapps(self):

        @handle_exception(ZeroDivisionError, None)
        def divide_function(a, b):
            return a / b

        self.assertEqual(5, divide_function(10, 2))
        self.assertRaises(ZeroDivisionError, divide_function, 10, 0)

    def test_attributeerror(self):
        self.fail = False

        def handler(e):
            self.fail = True

        @handle_exception(AttributeError, handler)
        def test_function():
            return 'hello'.some_attribute

        test_function()

        self.assert_(self.fail)

    def test_nonehandler(self):

        @handle_exception(AttributeError, None)
        def test_function():
            return 'hello'.some_attribute

        self.assertRaises(AttributeError, test_function)

    def test_noneexception(self):

        @handle_exception(None, None)
        def test_function():
            return 'hello'.some_attribute

        self.assertRaises(Exception, test_function)

if __name__ == '__main__':
    unittest.main()
