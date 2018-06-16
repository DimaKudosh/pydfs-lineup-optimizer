from distutils.core import setup

setup(
    name='pydfs-lineup-optimizer',
    version='2.0.0',
    packages=['pydfs_lineup_optimizer'],
    url='https://github.com/DimaKudosh/pydfs-lineup-optimizer',
    license='MIT',
    author='Dima Kudosh',
    author_email='dimakudosh@gmail.com',
    description='Tool for creating optimal lineups for daily fantasy sports',
    keywords=['dfs', 'fantasy', 'sport', 'lineup', 'optimize', 'optimizer', 'nba', 'nfl', 'nhl', 'mlb'],
    install_requires=['PuLP>=1.6.8', 'typing'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
