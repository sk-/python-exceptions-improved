import unittest

class ExampleTest(unittest.TestCase):
    def test_index(self):
        a = [1, 2]
        a[2]

    def test_key(self):
        a = {'foo': 1}
        a['fooo']

    def test_name(self):
        foo = 1
        fooo

    def test_attribute(self):
        a = ''
        a.Lower()


if __name__ == '__main__':
    unittest.main()
