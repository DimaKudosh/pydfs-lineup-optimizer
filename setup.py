import sys
from distutils.core import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name = 'pydfs-lineup-optimizer',
    version = '0.4.1',
    packages = ['tests', 'pydfs_lineup_optimizer', 'pydfs_lineup_optimizer.app'],
    url = 'https://github.com/DimaKudosh/pydfs-lineup-optimizer',
    license = '',
    author = 'Dima Kudosh',
    author_email = 'dimakudosh@gmail.com',
    description = 'Tool for creating optimal lineups for daily fantasy sports',
    keywords = ['dfs', 'fantasy', 'sport', 'lineup', 'optimize', 'optimizer'],
    install_requires = ['PuLP'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
)
