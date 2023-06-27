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
import os
import stat
import time
import traceback
import common.plugin.constants as const
from dateutil import parser
from common.plugin import MonitorPlugin, PluginResult
import common.api as API


class CheckFile( MonitorPlugin ):
    DEFAULT_TEMPLATE = """%if expired and exists:
The database file ${filename} is too old ${ datetime.fromtimestamp( ctime ).strftime( "%Y-%m-%d %H:%M:%S" ) }
must be less than ${} hours.
%elif exists:
% if context.get('size_valid', UNDEFINED) is not UNDEFINED:
  The database file ${filename} exist and is valid.
  The file size is invalid expected ${minimal_size}, file has ${size}.  
% else:
The database file ${filename} exist and is valid.
% endif
%elif exists:
The database file ${filename} exist and is valid.
%else:
The database file ${filename} doesn t exist.
%endif
"""

    def execute( self ):
        super().execute()
        task_result = PluginResult( self )
        filename = self.Attributes.get( 'filename' )
        attrs = { 'exists': False, 'expired': False, 'filename': filename, 'size_valid': True }
        if filename is not None:
            self.log.info( f"Testing {filename} for existance" )
            if os.path.exists( filename ):
                attrs[ 'exists' ] = True
                try:
                    stat_data = os.stat( filename )
                    res = True
                    attrs.update( {
                        'mode': stat.filemode( stat_data.st_mode ),
                        'ino': stat_data.st_ino,
                        'dev': stat_data.st_dev,
                        'nlink': stat_data.st_nlink,
                        'uid': stat_data.st_uid,
                        'gid': stat_data.st_gid,
                        'size': stat_data.st_size,
                        'atime': stat_data.st_atime,
                        'mtime': stat_data.st_mtime,
                        'ctime': stat_data.st_ctime,
                        'blocks': stat_data.st_blocks,
                    } )
                    minimal_size = self.Attributes.get( 'minimal_size' )
                    if isinstance( minimal_size, int ):
                        attrs[ 'minimal_size' ] = minimal_size
                        res = attrs[ 'size_valid' ] = stat_data.st_size >= minimal_size

                    expire = self.Attributes.get( 'expire' )
                    if expire:
                        if isinstance( expire, str ):
                            t = parser.parse( expire ).time()
                            expire = ( t.hour * 3600 ) + ( t.minute * 60 ) + t.second

                        if stat_data.st_ctime + expire < time.time():
                            msg = 'File exists, but is expired'
                            attrs[ 'expired' ] = True
                            res = False

                        else:
                            msg = 'File exists and is valid'

                    else:
                        msg = 'File exists'


                    task_result.update( res, msg, attrs )

                except Exception as exc:
                    task_result.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() },
                                           filename = filename )

            else:
                task_result.update( False, "Filename doesn't exist", attrs )

        else:
            task_result.update( False, "Filename not configured", attrs )

        API.QUEUE.put( task_result )
        return
