from distutils.core import setup

setup(
    name = 'pydfs-lineup-optimizer',
    version = '0.4',
    packages = ['tests', 'pydfs_lineup_optimizer', 'pydfs_lineup_optimizer.app'],
    url = 'https://github.com/DimaKudosh/pydfs-lineup-optimizer',
    license = '',
    author = 'Dima Kudosh',
    author_email = 'dimakudosh@gmail.com',
    description = 'Tool for creating optimal lineups for daily fantasy sports',
    keywords = ['dfs', 'fantasy', 'sport', 'lineup', 'optimize', 'optimizer'],
    install_requires = ['PuLP'],
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
)
