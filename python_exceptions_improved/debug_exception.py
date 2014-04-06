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
import os
import sys
import imp
import ast
import marshal
import difflib
import itertools
import re

import asm


class ModuleImporter(object):
    """
    Class that allows to patch modules.
    It is both a finder (find_module) and a loader (load_module).

    See PEP 302 (http://www.python.org/dev/peps/pep-0302/) for further details.
    """
    def __init__(self):
        self.install()

    def install(self):
        """Install this importer before all others."""
        if self not in sys.meta_path:
            sys.meta_path.insert(0, self)

    def uninstall(self):
        """Removes this importer from the global importers."""
        if self in sys.meta_path:
            sys.meta_path.remove(self)

    def get_module_from_package(self, name, file, file_path):
        if os.path.exists(os.path.join(file_path, '__init__.pyc')):
            return self.get_module_from_pyc(
                name, None, os.path.join(file_path, '__init__.pyc'))
        elif os.path.exists(os.path.join(file_path, '__init__.py')):
            return self.get_module_from_source(
                name, None, os.path.join(file_path, '__init__.py'))

    def get_module_from_source(self, name, file, file_path):
        try:
            if not file:
                file = open(file_path, 'U')
            code_tree = ast.parse(file.read())
            return self.get_module_from_code(
                name, compile(code_tree, file_path, 'exec'))
        finally:
            file.close()

    def get_module_from_pyc(self, name, file, file_path):
        try:
            if not file:
                file = open(file_path, 'rb')
            file.read(8)
            return self.get_module_from_code(name, marshal.load(file))
        finally:
            file.close()

    def get_module_from_code(self, module_name, module_code):
        module_code = asm.patch_code(module_code)
        mod = sys.modules.setdefault(module_name, imp.new_module(module_name))

        # The following two fields are required by PEP 302
        mod.__file__ = module_code.co_filename
        mod.__loader__ = self

        is_package = os.path.basename(mod.__file__) in ('__init__.py',
                                                        '__init__.pyc')
        if is_package:
            mod.__path__ = [os.path.dirname(mod.__file__)]
        package = get_package(module_name, is_package)
        if package:
            mod.__package__ = package
        exec module_code in mod.__dict__
        return mod

    def get_module(self, name, file, file_path, description):
        try:
            if description[2] == imp.PKG_DIRECTORY:
                return self.get_module_from_package(name, file, file_path)
            elif description[2] == imp.PY_SOURCE:
                return self.get_module_from_source(name, file, file_path)
            elif description[2] == imp.PY_COMPILED:
                return self.get_module_from_pyc(name, file, file_path)
        finally:
            if file:
                file.close()

    def find_module(self, module_name, path=None):  # pylint: disable=W0613
        """Returns self when the module registered is requested."""
        self.module_name = module_name
        if path:
            path_component = path[0].split('/')[::-1]
            module_component = module_name.split('.')
            for i in xrange(min(len(module_component), len(path_component))):
                if module_component[i] != path_component[i]:
                    break
            else:
                i += 1
            module_name = '.'.join(module_component[i:])
        result = imp.find_module(module_name, path)
        if result[2][2] in (imp.PKG_DIRECTORY, imp.PY_SOURCE, imp.PY_COMPILED):
            self.result = result
            return self

    def load_module(self, module_name):
        """Loads the registered module."""
        if self.module_name == module_name and self.result:
            return self.get_module(module_name, *self.result)
        else:
            raise ImportError('Module not found')


def get_package(module_name, is_package):
    """Returns a string representing the package to which the file belongs."""
    if is_package:
        return module_name
    else:
        return '.'.join(module_name.split('.')[:-1])


ATTRIBUTE_ERROR_MESSAGE_PATTERN = r"(')?(?P<type>[a-zA-Z0-9_]*)(')? (.*) has no attribute '(?P<attribute>[a-zA-Z0-9_]*)'"
ATTRIBUTE_ERROR_DELETE_MESSAGE_PATTERN = r"(?P<attribute>[a-zA-Z0-9_]*)"
NAME_ERROR_MESSAGE_PATTERN = r"global name '(?P<name>[a-zA-Z0-9_]*)' is not defined"


# TODO(skreft): Fix it for modules.
def name_to_class(class_name):
    matches = []
    for m in sys.modules.values():
        if hasattr(m, class_name):
            class_type = getattr(m, class_name)
            if isinstance(class_type, type):
                matches.append(class_type)
    if matches:
        return matches[0]


def is_similar_attribute(attribute, x):
    # N.B. foo and fox are not similar according to this
    attribute = attribute.lower().replace('_', '')
    x = x.lower().replace('_', '')
    return difflib.SequenceMatcher(a=attribute, b=x).ratio() >= 0.75


def get_similar_attributes(type, attribute):
    return itertools.ifilter(
        lambda x: is_similar_attribute(attribute, x), dir(type))


def get_similar_variables(name, variables):
    return itertools.ifilter(lambda x: is_similar_attribute(name, x), variables)


def get_debug_vars(tb):
    attr = None
    index = None
    attr_set = False
    index_set = False
    while tb:
        if '_s_attr' in tb.tb_frame.f_globals:
            attr = tb.tb_frame.f_globals['_s_attr']
            attr_set = True
            del tb.tb_frame.f_globals['_s_attr']
        if '_s_index' in tb.tb_frame.f_globals:
            index = tb.tb_frame.f_globals['_s_index']
            index_set = True
            tb.tb_frame.f_globals['_s_index']

        if attr_set or index_set:
            return attr, index, attr_set, index_set
        tb = tb.tb_next
    return None, None, False, False


class KeyError_(KeyError):
    def __str__(self):
        if len(self.args) > 1:
            return str(self.args)
        else:
            return str(self.args[0])


def debug_exceptions(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            et, ei, tb = sys.exc_info()
            msg = str(ei)
            if isinstance(ei, IndexError):
                attr, index, attr_set, index_set = get_debug_vars(tb.tb_next)
                if attr_set and index_set:
                    msg = msg + "\nDebug info:\n\tObject: %s\n\tObject len: %s\n\tIndex: %s" % (attr, len(attr), index)
            elif isinstance(ei, KeyError):
                attr, index, attr_set, index_set = get_debug_vars(tb.tb_next)
                if attr_set and index_set:
                    msg = msg + "\nDebug info:\n\tObject: %s\n\tKey: %s" % (attr, repr(index))
                et = KeyError_
                ei = KeyError_(msg)
            elif isinstance(ei, AttributeError):
                match = re.match(ATTRIBUTE_ERROR_MESSAGE_PATTERN, msg)
                field_type = None
                if match:
                    field_type = name_to_class(match.group('type'))
                    attribute = match.group('attribute')
                else:
                    match = re.match(ATTRIBUTE_ERROR_DELETE_MESSAGE_PATTERN, msg)
                    if match:
                        attribute =  match.group('attribute')
                attr, index, attr_set, index_set = get_debug_vars(tb.tb_next)
                if attr_set:
                    field_type = attr
                    debug_info = "\nDebug info:\n\tObject: %s\n\tType: %s\n\tAttributes: %s" % (repr(field_type), type(field_type), dir(field_type))
                elif field_type:
                    debug_info = "\nDebug info:\n\tType: %s\n\tAttributes: %s" % (field_type, dir(field_type))
                proposals = list(get_similar_attributes(field_type, attribute))
                if proposals:
                    msg += '. Did you mean %s?' % ', '.join(["'%s'" %a for a in proposals])
                msg = msg + debug_info
            elif isinstance(ei, NameError):
                match = re.match(NAME_ERROR_MESSAGE_PATTERN, msg)
                name = match.group('name')
                proposals = list(get_similar_variables(name, tb.tb_next.tb_frame.f_locals.keys() + tb.tb_next.tb_frame.f_globals.keys()))
                if proposals:
                    msg += '. Did you mean %s?' % ', '.join(["'%s'" %a for a in proposals])
            raise et(msg), None, tb.tb_next
    return wrapper


def decorate(f):
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        for method in result:
            setattr(args[1], method, debug_exceptions(getattr(args[1], method)))
        return result
    return wrapper
