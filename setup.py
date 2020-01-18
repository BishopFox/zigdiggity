#!/usr/bin/env python
# NOTE: See the README file for a list of dependencies to install.

import sys

try:
    from setuptools import setup, Extension
except ImportError:
    print("No setuptools found, attempting to use distutils instead.")
    from distutils.core import setup, Extension

err = []
warn = []
apt_get_pkgs = []
pip_pkgs = []

# TODO: Ideally we would detect missing python-dev and libgcrypt-dev to give better errors.

# Dot15d4 is a dep of some of the newer tools
try:
    from scapy.all import Dot15d4
except ImportError:
    warn.append("Scapy 802.15.4 (see README.md)")
    pip_pkgs.append("git+https://github.com/secdev/scapy.git#egg=scapy")

if len(err) > 0:
    print("""
Library requirements not met.  Install the following libraries, then re-run the setup script.

{}\n""".format('\n'.join(err)), file=sys.stderr)

if len(warn) > 0:
    print("""
Library recommendations not met. For full support, install the following libraries, then re-run the setup script.

{}\n""".format('\n'.join(warn)), file=sys.stderr)

if len(apt_get_pkgs) > 0 or len(pip_pkgs) > 0:
    print("The following commands should install these dependencies on Ubuntu, and can be adapted for other OSs:", file=sys.stderr)
    if len(apt_get_pkgs) > 0:
        print("\tsudo apt-get install -y {}".format(' '.join(apt_get_pkgs)), file=sys.stderr)
    if len(pip_pkgs) > 0:
        print("\tpip install {}".format(' '.join(pip_pkgs)), file=sys.stderr)

if len(err) > 0:
    sys.exit(1)

setup(name        = 'zigdiggity',
      version     = '2.1.0',
      description = 'Zigbee Framework and Tools for RaspBee',
      author = 'Peeps',
      author_email = 'a@b.c',
      license   = 'LICENSE',
      packages  = ['zigdiggity',
                   'zigdiggity/crypto',
                   'zigdiggity/datastore',
                   'zigdiggity/interface',
                   'zigdiggity/misc',
                   'zigdiggity/observers',
                   'zigdiggity/packets',
                   'zigdiggity/radios'],
      scripts = [],
      requires=['hexdump', 'pyserial(>=2.0)', 'pycryptodome', 'rangeparser', 'scapy', 'sqlalchemy'],
      )
