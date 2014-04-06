# Copyright 2013-2014 Sebastian Kreft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import new
import unittest

import python_exceptions_improved.asm as asm


def patch(f):
    return new.function(asm.patch_code(f.func_code), f.func_globals, f.func_name,
                        f.func_defaults, f.func_closure)


class Foo(object):
    def __init__(self):
        self.name = 'Foo'


class AsmTest(unittest.TestCase):
    def testSubscrBinary(self):
        def f():
            return [1, 2][1]
        self.assertEqual(f(), patch(f)())

        self.assertNotIn('_s_attr', globals())
        self.assertNotIn('_s_index', globals())

    def testSubscBinaryWithException(self):
        def f():
            {'1': 1}[0]
        with self.assertRaises(KeyError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual({'1': 1}, globals()['_s_attr'])
        self.assertIn('_s_index', globals())
        self.assertEqual(0, globals()['_s_index'])

    def testSubscrDelete(self):
        def f():
            a = {'1': 2}
            del a['1']
            return a
        self.assertEqual(f(), patch(f)())

        self.assertNotIn('_s_attr', globals())
        self.assertNotIn('_s_index', globals())

    def testSubscrDeleteWithException(self):
        def f():
            a = {'a': 'b'}
            del a['1']
        with self.assertRaises(KeyError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual({'a': 'b'}, globals()['_s_attr'])
        self.assertIn('_s_index', globals())
        self.assertEqual('1', globals()['_s_index'])

    def testSubscrStore(self):
        def f():
            a = [1, 2]
            a[0] = 2
            return a
        self.assertEqual(f(), patch(f)())

        self.assertNotIn('_s_attr', globals())
        self.assertNotIn('_s_index', globals())

    def testSubscrStoreWithException(self):
        def f():
            a = [1, 2]
            a[2] = 2
        with self.assertRaises(IndexError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual([1, 2], globals()['_s_attr'])
        self.assertIn('_s_index', globals())
        self.assertEqual(2, globals()['_s_index'])

    def testNested_SubscrStoreWithException(self):
        def f():
            a = [1, 2]
            b = [2, 3, 4]
            c = 0
            return a[b[c]]
        with self.assertRaises(IndexError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual([1, 2], globals()['_s_attr'])
        self.assertIn('_s_index', globals())
        self.assertEqual(2, globals()['_s_index'])

    def testInnerCode_SubscrStoreWithException(self):
        def f():
            def g():
                a = [1, 2]
                a[2] = 2
            return g()
        with self.assertRaises(IndexError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual([1, 2], globals()['_s_attr'])
        self.assertIn('_s_index', globals())
        self.assertEqual(2, globals()['_s_index'])

    def testAttrLoad(self):
        def f():
            o = Foo()
            return o.name
        self.assertEqual(f(), patch(f)())

        self.assertNotIn('_s_attr', globals())
        self.assertNotIn('_s_index', globals())

    def testAttrLoadWithException(self):
        o = Foo()
        def f():
            return o.names
        with self.assertRaises(AttributeError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual(o, globals()['_s_attr'])
        self.assertNotIn('_s_index', globals())

    def testAttrDelete(self):
        def f():
            o = Foo()
            del o.name
        self.assertEqual(f(), patch(f)())

        self.assertNotIn('_s_attr', globals())
        self.assertNotIn('_s_index', globals())

    def testAttrDeleteWithException(self):
        o = Foo()
        def f():
            del o.names
        with self.assertRaises(AttributeError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual(o, globals()['_s_attr'])
        self.assertNotIn('_s_index', globals())

    def testAttrStore(self):
        def f():
            o = Foo()
            o.var = 1
        self.assertEqual(f(), patch(f)())

        self.assertNotIn('_s_attr', globals())
        self.assertNotIn('_s_index', globals())

    def testAttrStoreWithException(self):
        o = object()
        def f():
            o.var = 1
        with self.assertRaises(AttributeError):
            patch(f)()

        self.assertIn('_s_attr', globals())
        self.assertEqual(o, globals()['_s_attr'])
        self.assertNotIn('_s_index', globals())


if __name__ == '__main__':
    unittest.main()
