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
class Foo(object):
    def __init__(self):
        self.name = 'Foo'


def subscr_binary():
    a = []
    a[0]


def subscr_store():
    a = []
    a[0] = 1


def subscr_delete():
    a = []
    del a[0]


def attr_load():
    o = Foo()
    o.names


def attr_store():
    o = object()
    o.name = 'bla'


def attr_delete():
    o = Foo()
    del o.names
