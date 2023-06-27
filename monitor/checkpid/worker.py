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
import traceback
from common.plugin import MonitorPlugin, PluginResult
import common.plugin.constants as const
from common.checkpid import checkPidFilename
import common.api as API


class CheckPid( MonitorPlugin ):
    def execute( self ):
        super().execute(  )
        task_result = PluginResult( self )
        try:
            filename = self.Attributes.get( const.C_FILENAME )
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
                                    "ctime": stat_data.st_ctime,
                                    "blocks": stat_data.st_blocks }

                    presult, pid = checkPidFilename( filename )
                    # now check if the PID exists
                    if not presult:
                        task_result.update( False, f"process does not exist", pidFileData, filename = filename, pid = pid )

                    else:
                        task_result.update( True, f"process exists", pidFileData, filename = filename, pid = pid )

                else:
                    task_result.update( False, "Filename doesn't exist" )

            else:
                task_result.update( False, "Filename not configured" )

        except Exception as exc:
            task_result.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() } )

        API.QUEUE.put( task_result )
        return
