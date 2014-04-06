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
import importlib
import unittest

import python_exceptions_improved.debug_exception as debug_exception


class DebugExceptionsTest(unittest.TestCase):
    def testNameErrorLocals(self):
        @debug_exception.debug_exceptions
        def f():
            var = ''
            vari

        with self.assertRaises(NameError) as ctx:
            f()

        self.assertIn('Did you mean \'var\'', str(ctx.exception))

    def testNameErrorGlobals(self):
        @debug_exception.debug_exceptions
        def f():
            unittest2

        with self.assertRaises(NameError) as ctx:
            f()

        self.assertIn('Did you mean \'unittest\'', str(ctx.exception))

    def testIndexError(self):
        @debug_exception.debug_exceptions
        def f():
            a = [1, 2]
            a[2]

        globals()['_s_attr'] = [1, 2]
        globals()['_s_index'] = 2
        with self.assertRaises(IndexError) as ctx:
            f()

        self.assertIn('Debug info:\n\tObject: [1, 2]\n\tObject len: 2\n\tIndex: 2', str(ctx.exception))

    def testIndexErrorNoGlobals(self):
        @debug_exception.debug_exceptions
        def f():
            a = [1, 2]
            a[2]

        if '_s_attr' in globals():
            del globals()['_s_attr']
        with self.assertRaises(IndexError) as ctx:
            f()

        self.assertEqual('list index out of range', str(ctx.exception))

    def testKeyError(self):
        @debug_exception.debug_exceptions
        def f():
            a = {}
            a['bla']

        globals()['_s_attr'] = {}
        globals()['_s_index'] = 'bla'
        with self.assertRaises(KeyError) as ctx:
            f()

        self.assertIn('Debug info:\n\tObject: {}\n\tKey: \'bla\'', ctx.exception.message)

    def testKeyErrorNoGlobals(self):
        @debug_exception.debug_exceptions
        def f():
            a = {}
            a['bla']

        if '_s_attr' in globals():
            del globals()['_s_attr']
        with self.assertRaises(KeyError) as ctx:
            f()

        self.assertIn('bla', ctx.exception.message)


    def testAttributeError(self):
        @debug_exception.debug_exceptions
        def f():
            a = ''
            a.Lower()

        globals()['_s_attr'] = ''
        with self.assertRaises(AttributeError) as ctx:
            f()

        self.assertIn('Did you mean \'islower\', \'lower\'', str(ctx.exception))
        self.assertIn('Debug info:\n\tObject: \'\'\n\tType: <type \'str\'>\n\tAttributes: ', str(ctx.exception))

    def testAttributeErrorNoGlobals(self):
        @debug_exception.debug_exceptions
        def f():
            a = ''
            a.Lower()

        if '_s_attr' in globals():
            del globals()['_s_attr']
        with self.assertRaises(AttributeError) as ctx:
            f()

        self.assertIn('Did you mean \'islower\', \'lower\'', str(ctx.exception))
        self.assertIn('Debug info:\n\tType: <type \'str\'>\n\tAttributes: ', str(ctx.exception))


class ModuleImporterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        debug_exception.ModuleImporter()
        cls.foo = importlib.import_module('foo_data')

    def testSubscrBinary(self):
        with self.assertRaises(IndexError) as ctx:
            debug_exception.debug_exceptions(self.foo.subscr_binary)()
        self.assertIn('Debug info:\n\tObject: []\n\tObject len: 0\n\tIndex: 0', str(ctx.exception))

    def testSubscrStore(self):
        with self.assertRaises(IndexError) as ctx:
            debug_exception.debug_exceptions(self.foo.subscr_store)()
        self.assertIn('Debug info:\n\tObject: []\n\tObject len: 0\n\tIndex: 0', str(ctx.exception))

    def testSubscrDelete(self):
        with self.assertRaises(IndexError) as ctx:
            debug_exception.debug_exceptions(self.foo.subscr_delete)()
        self.assertIn('Debug info:\n\tObject: []\n\tObject len: 0\n\tIndex: 0', str(ctx.exception))

    def testAttrrLoad(self):
        with self.assertRaises(AttributeError) as ctx:
            debug_exception.debug_exceptions(self.foo.attr_load)()
        self.assertIn('Debug info:', str(ctx.exception))
        self.assertIn('\n\tObject: ', str(ctx.exception))
        self.assertIn('\n\tType: <class \'foo_data.Foo\'>\n\tAttributes: ', str(ctx.exception))

    def testAttrrDelete(self):
        with self.assertRaises(AttributeError) as ctx:
            debug_exception.debug_exceptions(self.foo.attr_delete)()
        self.assertIn('Debug info:', str(ctx.exception))
        self.assertIn('\n\tObject: ', str(ctx.exception))
        self.assertIn('\n\tType: <class \'foo_data.Foo\'>\n\tAttributes: ', str(ctx.exception))

    def testAttrStore(self):
        with self.assertRaises(AttributeError) as ctx:
            debug_exception.debug_exceptions(self.foo.attr_store)()
        self.assertIn('Debug info:', str(ctx.exception))
        self.assertIn('\n\tObject: ', str(ctx.exception))
        self.assertIn('\n\tType: <type \'object\'>\n\tAttributes: ', str(ctx.exception))

if __name__ == '__main__':
    unittest.main()
