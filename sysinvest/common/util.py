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
import re


def time2seconds( value: str ):
    expr = re.compile( '(\d+)' )
    result = expr.findall( value )
    if len( result ) == 1:
        seconds = int( result[0] )

    elif len(result) == 2:
        seconds = ( int( result[ 0 ] ) * 60 ) + int( result[ 1 ] )

    elif len( result ) == 3:
        seconds = ( int( result[ 0 ] ) * 3600 ) + ( int( result[ 1 ] ) * 60) + int( result[ 2 ] )

    else:
        raise Exception( "Invalid time format" )

    return seconds
