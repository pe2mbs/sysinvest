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
import distro
import platform as pyplatform


platform = None
""" Current platform """

platform_unmapped = None
""" Current platform without "Ubuntu is Debian"-like mapping """

platform_string = None

def detect_platform():
    release = pyplatform.release()
    platform = pyplatform.system()
    version = pyplatform.version()

    global platform_unmapped, platform_string
    if platform == 'Windows':
        dist = platform.lower()                         # windows
        platform_unmapped = f'{platform.lower()}'
        platform_string = f'{platform} {version} {release}'

    elif platform == 'Linux':
        dist = distro.id()                              # any linux distro
        platform_unmapped = distro.name()
        platform_string = distro.name( pretty=True )

    elif platform == 'Darwin':
        dist = 'osx'                                    # osx
        platform_unmapped = distro.name()
        platform_string = distro.name( pretty=True )

    elif platform == 'Java':
        dist = 'java'                                   # java
        platform_unmapped = 'java'
        platform_string = 'java'

    else:
        raise Exception( f'Unknown system platform: {platform}' )

    return dist, platform_unmapped


def platform_select( **values ):
    """
    Selects a value from **kwargs** depending on runtime platform

        service = platform_select(
            debian='samba',
            ubuntu='smbd',
            centos='smbd',
            default='samba',
        )

    """
    if platform_unmapped in values:
        return values[ platform_unmapped ]

    if platform in values:
        return values[ platform ]

    return values.get( 'default', None )

