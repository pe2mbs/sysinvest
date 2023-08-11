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
import psutil
import traceback
from sysinvest.common.plugin import MonitorPlugin
import sysinvest.common.plugin.constants as const
from sysinvest.common.checkpid import checkPidFilename
import sysinvest.common.api as API


class CheckPid( MonitorPlugin ):
    DEFAULT_TEMPLATE = """${message}
%if context.get('mtime', UNDEFINED) is not UNDEFINED:
Filename: ${filename} PID ${pid} created ${ datetime.fromtimestamp( mtime ).strftime( "%Y-%m-%d %H:%M:%S" ) }
%else:
Filename: ${filename} PID ${pid}
%endif
%if context.get('msg', UNDEFINED) is not UNDEFINED:
% for item in msg:
${item} 
% endfor
%endif
"""

    def execute( self ):
        super().execute(  )
        try:
            filename = self.Attributes.get( const.C_FILENAME )
            self.log.info( f"Checking PID file: {filename}")
            if filename:
                if os.path.exists( filename ):
                    stat_data = os.stat( filename )
                    pidFileData = { "mode": stat_data.st_mode,
                                    "ino": stat_data.st_ino,
                                    "dev": stat_data.st_dev,
                                    "nlink": stat_data.st_nlink,
                                    "uid": stat_data.st_uid,
                                    "gid": stat_data.st_gid,
                                    "size": stat_data.st_size,
                                    "atime": stat_data.st_atime,
                                    "mtime": stat_data.st_mtime,
                                    "ctime": stat_data.st_ctime }
                    # now check if the PID exists
                    presult, pid = checkPidFilename( filename )
                    if not presult:
                        self.update( False, f"process does not exist", pidFileData, filename = filename, pid = pid )

                    else:
                        process = psutil.Process( pid )
                        executable = self.Attributes.get( 'executable' )
                        if isinstance( executable, str ):
                            cmdline = process.cmdline()
                            if cmdline[ 0 ] == executable:
                                commandline = self.Attributes.get( 'commandline' )
                                if isinstance( commandline, str ):
                                    commandline = commandline.split( ' ' )

                                if isinstance( commandline, ( list, tuple ) ):
                                    msg = []
                                    for cmd in commandline:
                                        if cmd not in cmdline:
                                            msg.append( f"{cmd} not found in command line" )

                                    if len( msg ) == 0:
                                        cmdline = ' '.join(cmdline)
                                        self.update( True, f"process exists: {cmdline}", pidFileData,
                                                            filename=filename, pid=pid)

                                    else:
                                        cmdline = ' '.join( cmdline )
                                        self.update( False, f"process exists, but has invalid command line: {cmdline}", pidFileData,
                                                            msg = msg, filename=filename, pid=pid)

                                else:
                                    cmdline = ' '.join(cmdline)
                                    self.update(False,
                                                       f"process exists, but has invalid executable line: {cmdline}",
                                                       pidFileData, filename=filename, pid=pid)

                        else:
                            self.update( True, f"process exists", pidFileData, filename = filename, pid = pid )

                else:
                    self.update( False, "Filename doesn't exist" )

            else:
                self.update( False, "Filename not configured" )

        except Exception as exc:
            self.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() } )

        API.QUEUE.put( self )
        return
