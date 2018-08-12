try:
    from setuptools import setup, Extension
except ImportError:
    print("No setuptools found, attempting to use distutils instead.")
    from distutils.core import setup, Extension

import distutils.cmd
import distutils.log
import subprocess
import sys

class InstallScapyCommand(distutils.cmd.Command):
    def run(self):
        command = ['scripts/install_scapy.sh']
        subprocess.check_call(command)

zigbee_transkey = Extension('zigbee_transkey',
                    sources = ['crypt/zigbee_transkey.c'],
                    libraries = ['gcrypt'],
                    include_dirs = ['/usr/local/include', '/usr/include', '/sw/include/', 'crypt'],
                    library_dirs = ['/usr/local/lib', '/usr/lib','/sw/var/lib/']
                    )

setup  (name        = 'zigdiggity',
        version     = '1.0.0',
        description = 'ZigBee Hacking Toolkit',
        author = 'Matthew Gleason',
        author_email = '***REMOVED***',
        license   = 'LICENSE.txt',
        packages  = ['zigdiggity', 'zigdiggity.interface', 'zigdiggity.utils', 'zigdiggity.datastore'],
        requires = ['killerbee'], 
        scripts = ['tools/zigdig_ackattack', 'tools/zigdig_ackattack_minimal', 'tools/zigdig_cleardevices', 'tools/zigdig_clearall','tools/zigdig_clearnetworks', 'tools/zigdig_blackhole', 'tools/zigdig_blackhole_aggressive', 'tools/zigdig_insecurerejoin'],
        install_requires=['killerbee>=2.6.1'],
        ext_modules = [ zigbee_transkey ],
        )

