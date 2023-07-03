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

def sizeof2shorthand( num: int, suffix: str = "B" ):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs( num ) < 1000.0:
            return f"{num:3.1f}{unit}{suffix}"

        num /= 1000.0

    return f"{num:.1f}Yi{suffix}"

def shorthand2sizeof( num: str, suffix: str = "B" ):
    number = 0.0
    sizedesc = ''
    for idx, ch in enumerate( num ):
        if not ch.isdigit() and ch not in (',', '.'):
            number = float( num[:idx].replace( ',', '.' ) )
            sizedesc = num[idx:]
            break

    if sizedesc == '':
        return int( number )


    for unit in ("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        number *= 1000.0
        if sizedesc.startswith( unit ):
            break

    return int( number )


if __name__ == '__main__':
    short = sizeof2shorthand( 2957351410 )
    print( short )
    result = shorthand2sizeof( short )
    print( result )






