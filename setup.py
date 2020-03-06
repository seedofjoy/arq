from pathlib import Path

from importlib.machinery import SourceFileLoader
from setuptools import setup

readme = Path(__file__).parent.joinpath('README.rst')
if readme.exists():
    with readme.open() as f:
        long_description = f.read()
else:
    long_description = '-'
# avoid loading the package before requirements are installed:
version = SourceFileLoader('version', 'darq/version.py').load_module()

setup(
    name='darq',
    version=str(version.VERSION),
    description='Job queues in python with asyncio and redis.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Typing :: Typed',
    ],
    python_requires='>=3.6',
    author='Igor Mozharovsky',
    author_email='igor.mozharovsky@gmail.com',
    url='https://github.com/seedofjoy/darq',
    license='MIT',
    packages=['darq'],
    package_data={'darq': ['py.typed']},
    zip_safe=True,
    entry_points="""
        [console_scripts]
        darq=darq.cli:cli
    """,
    install_requires=[
        'async-timeout>=3.0.0',
        'aioredis>=1.1.0',
        'click>=6.7',
        'pydantic>=0.20',
        'dataclasses>=0.6;python_version == "3.6"'
    ],
    extras_require={
        'watch': ['watchgod>=0.4'],
    }
)
