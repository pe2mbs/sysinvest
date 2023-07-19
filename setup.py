# -*- coding: utf-8 -*-
#
#   sysinvest - Python system monitor and investigation utility
#   Copyright (C) 2022-2023 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
#
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License GPL-2.0-only
#   as published by the Free Software Foundation; only version 2 of the
#   License.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License GPL-2.0-only along with this library; if not, write to the
#   Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301 USA
#
from setuptools import setup, find_packages
import codecs
import os.path

class GetPackageDetails( object ):
    def __init__( self, rel_path: str ):
        self.package        = None
        self.description    = None
        self.version        = None
        self.date           = None
        self.author         = None
        self.author_email   = None
        self.copyright      = None
        self.licence        = None
        self.get_details( rel_path )
        return

    def read( self, rel_path ):
        here = os.path.abspath( os.path.dirname( __file__ ) )
        with codecs.open(os.path.join(here, rel_path), 'r') as fp:
            return fp.read()

    def get_details( self, rel_path ):
        for line in self.read( rel_path ).splitlines():
            print( line )
            if '=' in line:
                args = line.split( '=' )
                if len( args ) == 2:
                    name = args[0].strip()
                    if not hasattr( self, name ):
                        raise Exception( f"{name} is not known attribute" )

                    setattr( self, name, args[1].strip(' \'"') )


        return

package = GetPackageDetails( 'sysinvest/version.py' )

setup(
    name=package.package,
    version=package.version,
    description=package.description,
    long_description=open('README.md').read(),
    license=package.licence,
    classifiers = [
        "Intended Audience :: Application managers",
        'License :: GNU GENERAL PUBLIC LICENSE v2',
        "Programming Language :: Python :: 3.8",
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Linux',
    ],
    url="https://github.com/pe2mbs/sysinvest",
    project_urls={
        "Documentation": "https://github.com/pe2mbs/sysinvest",
        "Source": "https://github.com/pe2mbs/sysinvest",
    },
    author=package.author,
    author_email=package.author_email,
    install_requires=[
        'Mako',
        'psutil',
        'python-dateutil',
        'PyYAML',
        'pycron',
        'importlib-metadata; python_version >= "3.8"'
    ],
    include_package_data=True,
    package_data={ "": [ "*.md", "*.mako" ],
                   "sysinvest": [ 'template/*.*', 'sysinvest/report/template_index.mako' ],
                   },
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sysInvest=sysinvest.__main__:main',
        ]
    }

)
