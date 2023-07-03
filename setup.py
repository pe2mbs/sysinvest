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


setup(
    name='sysinvest',
    version='0.2.0',
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
                   "sysinvest/template": [ "*.mako" ] },
    packages=find_packages(
        # All keyword arguments below are optional:
        where='',  # '.' by default
        include=[ 'sysinvest*' ],  # ['*'] by default
    ),
    entry_points={
        'console_scripts': [
            'sysInvest = sysinvest.__main__:main',
        ]
    }

)
