#!/usr/bin/env python
#
# Versioning routines:
# Idea from http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
# Code from https://github.com/warner/python-ecdsa/blob/0ed702a9d4057ecf33eea969b8cf280eaccd89a1/setup.py#L34
# Altered to support any version tagging convention and version.py location.
#

# Make sure setup.py can work with no setuptools installed initially.
# See ez_setup.py for details (this trick is part of easyinstall).
from ez_setup import use_setuptools
use_setuptools()

import os, sys, subprocess, re
from setuptools import setup, find_packages, Command
from setuptools.command.sdist import sdist as _sdist

VERSION_PY_PATH = "tootwi/_version.py"
VERSION_PY_TEXT = """
# This file is generated from Git information by running 'setup.py version'.
# Distribution tarballs contain a pre-generated copy of this file.
__version__ = '%s'
"""

def update_version_py():
    if not os.path.isdir(".git"):
        print "This does not appear to be a Git repository."
        return
    try:
        p = subprocess.Popen(["git", "describe", "--dirty", "--always"],
                             stdout=subprocess.PIPE)
    except EnvironmentError:
        print "unable to run git, leaving %s alone" % (VERSION_PY_PATH)
        return
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print "unable to run git, leaving %s alone" % (VERSION_PY_PATH)
        return
    
    # Extract version info from git tag and put it into a file.
    stdout = stdout.strip()
    matches = re.match(r'^\D*?(\d+\.\d+.*?)$', stdout, re.X + re.S)
    if not matches:
        print "unable to find version info in tag %s, leaving %s alone" % (stdout, VERSION_PY_PATH)
        return
    else:
        ver = matches.group(1)
        f = open(VERSION_PY_PATH, "w")
        f.write(VERSION_PY_TEXT % ver)
        f.close()
        print "set %s to '%s'" % (VERSION_PY_PATH, ver)

def get_version():
    try:
        f = open(VERSION_PY_PATH)
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match(r"__version__ = '([^']+)'", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None

class version(Command):
    description = "update _version.py from Git repo"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        update_version_py()
        print "Version is now", get_version()

class sdist(_sdist):
    def run(self):
        update_version_py()
        # unless we update this, the sdist command will keep using the old version
        self.distribution.metadata.version = get_version()
        return _sdist.run(self)


def read(filename):
    """Used to read README file below."""
    return file(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    # Packaging information.
    name='tootwi',
    version=get_version(),
    
    # Maintenance and code layout information
    package_dir = {'': 'src'},
    packages=find_packages('src', exclude=['tests']),
    test_suite='tests',
    cmdclass={ 'version': version, 'sdist': sdist },
    
    # Descriptive information.
    url='http://github.com/nolar/tootwi',
    author='Sergey Vasilyev',
    author_email='nolar@nolar.info',
    license='BSD',
    keywords='twitter api oop object-oriented oauth stream streams',
    description='Twitter API object-oriented library (pure python)',
    long_description=read('README'),
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
