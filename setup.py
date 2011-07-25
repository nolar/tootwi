#!/usr/bin/env python

# Make sure setup.py can work with no setuptools installed initially.
# See ez_setup.py for details (this trick is a part of easyinstall).
from ez_setup import use_setuptools
use_setuptools()

# Now, our own stuff.
import os
import sys
from setuptools import setup, find_packages
from version import get_version

#
# Version and overrided sdist commands:
# Idea from http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
# Code from https://github.com/warner/python-ecdsa/blob/0ed702a9d4057ecf33eea969b8cf280eaccd89a1/setup.py#L34
#
from setuptools import Command
from setuptools.command.sdist import sdist as _sdist

class version(Command):
    description = "update version file from Git repo"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        print "Version is now", get_version(force_update=True)

class sdist(_sdist):
    def run(self):
        # unless we update this, the sdist command will keep using the old version
        self.distribution.metadata.version = get_version(allow_update=True)
        return _sdist.run(self) #NB: this is an old-style class, not supported by super()


def read(filename):
    """Used to read README file below."""
    return file(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    # Packaging information.
    name='tootwi',
    version=get_version(),
    
    # Maintenance and code layout information.
    packages=find_packages(exclude=['tests']),
    test_suite='tests',
    tests_require=[] + (['unittest2'] if sys.version_info < (3,) else []),
    install_requires=['oauth2'],
    #extras_require={
    #    'oauth-authorization': ['oauth2'],
    #    'basic-authorization': [],
    #    'urllib-transport': [],
    #    'pycurl-transport': ['pycurl'],
    #    'json-format': [],
    #    'lxml-format': ['lxml'],
    #},
    cmdclass={ 'version': version, 'sdist': sdist },
    
    # Descriptive information used for registering.
    url='http://github.com/nolar/tootwi',
    author='Sergey Vasilyev',
    author_email='nolar@nolar.info',
    license='BSD',
    keywords='twitter api oop object-oriented oauth stream streams',
    description='Twitter API object-oriented library (pure python)',
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'License :: Freeware',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
