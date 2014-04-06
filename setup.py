#!/usr/bin/env python
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

from setuptools import setup, find_packages

setup(
    name='python-exceptions-improved',
    version='0.1',
    description='Wrapper to enhance exceptions data',
    author='Sebastian Kreft',
    url='http://github.com/sk-/python-exceptions-improved',
    packages=find_packages(exclude=['test']),
    scripts=[
        'scripts/test-exceptions-wrapper.py',
    ],
    install_requires=['byteplay'],
    tests_require=['nose', 'coverage'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
    ],
)
