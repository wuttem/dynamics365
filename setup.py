#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools.command.test import test as TestCommand
import sys
import os
import re

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as readme_file:
    readme = readme_file.read()


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)

# reqs is a list of requirement
reqs = [str(ir.req) for ir in install_reqs]

test_requirements = [
    "pytest", "mock"
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='dynamics365',
    version="0.1",
    description="Dynamics 365 API Client",
    long_description=readme,
    author="Matthias Wutte",
    author_email='matthias.wutte@gmail.com',
    url='https://github.com/wuttem',
    packages=[
        'dynamics365',
    ],
    package_dir={'dynamics365':
                 'dynamics365'},
    include_package_data=True,
    install_requires=reqs,
    zip_safe=False,
    keywords='dynamics',
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
)
