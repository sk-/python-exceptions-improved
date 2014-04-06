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
import byteplay as bp


def patch_code(code):
    """Recursively patches a code object to store variables for later debugging.

    This will replace the bytecode as follow:
    - if the opcode is in (BINARY_SUBCSR, STORE_SUBSCR, DELETE_SUBSCR) it will
      add DUP_TOPX, 2
          STORE_GLOBAL, '_s_index'
          STORE_GLOBAL, '_s_attr'
      before calling the opcode. This will save the key and object for later
      use. Then it will call the opcode. And finally will
      clean the added variables with
          DELETE_GLOBAL, '_s_index'
          DELETE_GLOBAL, '_s_attr'
    - if the opcode is in (LOAD_ATTR, STORE_ATTR, DELETE_ATTR) it will
      add DUP_TOP, None
          STORE_GLOBAL, '_s_attr'
      before calling the opcode. This will save the object for later
      use. Then it will call the opcode. And finally will
      clean the added variable with
          DELETE_GLOBAL, '_s_attr'

     This means that if the code is not interrumped, nothing will change
     (unless of course the added variables collide with predefined ones).

     The interesting part is when an exception is raised when calling the
     opcode. In this case the exception handling code can analyze the stored
     values and print more useful information to the user.

    Args:
      code: a types.CodeType object. It may represent a function, module, etc.

    Returns:
      a new patched code object.
    """
    f_code = bp.Code.from_code(code)
    f_code = patch_bp_code(f_code)
    return f_code.to_code()


def patch_bp_code(f_code):
    """Helper function to patch a bp.Code object.

    Args:
      f_code: an byteplay.Code object

    Returns:
      a new patched object (see patch_code for details).
    """
    code = []
    for op in f_code.code:
        if op[0] in (bp.BINARY_SUBSCR, bp.STORE_SUBSCR, bp.DELETE_SUBSCR):
            code.extend([(bp.DUP_TOPX, 2),
                         (bp.STORE_GLOBAL, '_s_index'),
                         (bp.STORE_GLOBAL, '_s_attr')])
            code.append(op)
            code.extend([(bp.DELETE_GLOBAL, '_s_index'),
                         (bp.DELETE_GLOBAL, '_s_attr')])
        elif op[0] in (bp.LOAD_ATTR, bp.STORE_ATTR, bp.DELETE_ATTR):
            code.extend([(bp.DUP_TOP, None),
                         (bp.STORE_GLOBAL, '_s_attr')])
            code.append(op)
            code.extend([(bp.DELETE_GLOBAL, '_s_attr')])
        elif op[0] == bp.LOAD_CONST:
            if isinstance(op[1], bp.Code):
                code.append((op[0], patch_bp_code(op[1])))
            else:
                code.append(op)
        else:
            code.append(op)
    f_code.code = code
    return f_code
