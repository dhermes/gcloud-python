# Copyright 2017 Google Inc.
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

from __future__ import absolute_import

import os

import nox
import nox.command


# NOTE: The following should be used eventually:
LOCAL_DEPS = (
    os.path.join('..', 'core'),
)


@nox.session
@nox.parametrize('python_version', ['2.7', '3.4', '3.5', '3.6'])
def unit_tests(session, python_version):
    """Run the unit test suite."""

    # Run unit tests against all supported versions of Python.
    session.interpreter = 'python{}'.format(python_version)

    # Set the virtualenv dirname.
    session.virtualenv_dirname = 'unit-' + python_version

    # Install all test dependencies, then install this package in-place.
    session.install('mock', 'pytest', 'pytest-cov', *LOCAL_DEPS)
    session.install('-e', '.')

    # Run py.test against the unit tests.
    session.run(
        'py.test',
        '--quiet',
        '--cov=google.cloud.firestore',
        '--cov=google.cloud.firestore_v1beta1',
        '--cov=tests.unit',
        '--cov-append',
        '--cov-config=.coveragerc',
        '--cov-report=',
        '--cov-fail-under=97',
        os.path.join('tests', 'unit'),
        *session.posargs
    )


@nox.session
@nox.parametrize('python_version', ['2.7', '3.6'])
def system_tests(session, python_version):
    """Run the system test suite."""
    # Sanity check: Only run system tests if the environment variable is set.
    if not os.environ.get('FIRESTORE_APPLICATION_CREDENTIALS'):
        session.skip('Credentials must be set via environment variable.')

    # Run the system tests against latest Python 2 and Python 3 only.
    session.interpreter = 'python{}'.format(python_version)

    # Set the virtualenv dirname.
    session.virtualenv_dirname = 'sys-' + python_version

    # Install all test dependencies, then install this package into the
    # virtualenv's dist-packages.
    session.install('mock', 'pytest', 'pytest-cov', *LOCAL_DEPS)
    session.install(os.path.join('..', 'test_utils'))
    session.install('.')

    fail_under = 50
    # Don't collide with standard .coverage used in
    # ``unit_tests()`` and ``cover()``.
    env = {'COVERAGE_FILE': '.sys-test-coverage'}
    # Run py.test against the system tests.
    args = (
        'py.test',
        '--cov=google.cloud.firestore',
        '--cov=google.cloud.firestore_v1beta1',
        '--cov-config=.coveragerc',
        '--cov-report=',
        '--cov-fail-under={:d}'.format(fail_under),
        os.path.join('tests', 'system.py'),
    )
    args += session.posargs
    session.run(*args, **{'env': env})
    # Display the coverage report.
    session.run(
        'coverage',
        'report',
        '--show-missing',
        '--fail-under={:d}'.format(fail_under),
        env=env,
    )
    # Erase the coverage files created.
    session.run('coverage', 'erase', env=env)


@nox.session
def lint(session):
    """Run flake8.

    Returns a failure if flake8 finds linting errors or sufficiently
    serious code quality issues.
    """
    session.interpreter = 'python3.6'
    session.install('flake8', 'pylint', 'gcp-devrel-py-tools', *LOCAL_DEPS)
    session.install('.')
    session.run('flake8', os.path.join('google', 'cloud', 'firestore'))
    session.run(
        'gcp-devrel-py-tools', 'run-pylint',
        '--config', 'pylint.config.py',
        '--library-filesets', 'google',
        '--test-filesets', 'tests',
        # Temporarily allow this to fail.
        success_codes=range(0, 100))


@nox.session
def lint_setup_py(session):
    """Verify that setup.py is valid (including RST check)."""
    session.interpreter = 'python3.6'

    # Set the virtualenv dirname.
    session.virtualenv_dirname = 'setup'

    session.install('docutils', 'Pygments')
    session.run(
        'python', 'setup.py', 'check', '--restructuredtext', '--strict')


@nox.session
def cover(session):
    """Run the final coverage report.

    This outputs the coverage report aggregating coverage from the unit
    test runs (not system test runs), and then erases coverage data.
    """
    session.interpreter = 'python3.6'
    session.chdir(os.path.dirname(__file__))
    session.install('coverage', 'pytest-cov')
    session.run('coverage', 'report', '--show-missing', '--fail-under=100')
    session.run('coverage', 'erase')
