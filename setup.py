import os
from setuptools import setup, find_packages


exec(open('pydfs_lineup_optimizer/version.py').read())


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pydfs-lineup-optimizer',
    version=__version__,
    packages=find_packages(exclude=['tests*']),
    url='https://github.com/DimaKudosh/pydfs-lineup-optimizer',
    license='MIT',
    author='Dima Kudosh',
    author_email='dimakudosh@gmail.com',
    description='Tool for creating optimal lineups for daily fantasy sports',
    keywords=['dfs', 'fantasy', 'sport', 'lineup', 'optimize', 'optimizer', 'nba', 'nfl', 'nhl', 'mlb'],
    install_requires=['PuLP>=1.6.8', 'typing', 'pytz'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
