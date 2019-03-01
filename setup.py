# -*- coding: utf-8 -*-

import sys

from setuptools import (
    find_packages,
    setup,
)
from setuptools.command.test import test as TestCommand


def get_install_requires(requirements_file='requirements.txt'):
    """
    parse requirements.txt, ignore links, exclude comments
    """
    requirements = []
    for line in open(requirements_file).readlines():
        # skip to next iteration if comment or empty line
        if line.startswith('#') or line == '' or line.startswith('http') \
                or line.startswith('git'):
            continue
        # add line to requirements
        requirements.append(line)
    return requirements


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', '-q')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='money',
      version='1',
      description='Money WebApp',
      author='Paweł Sadowski',
      author_email='sadziu@ithaca.pl',
      packages=[
          'money',
      ],
      package_dir={},
      scripts=[
      ],
      package_data={
      },
      install_requires=get_install_requires('requirements.txt'),
      tests_require=get_install_requires('requirements-dev.txt'),
      cmdclass={'test': PyTest},
      )
