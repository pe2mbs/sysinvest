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
from datetime import datetime
from sysinvest.common.interfaces import FileExists, TaskStatus, ExceptionData
from sysinvest.common.util import time2seconds
from sysinvest.common.plugin_agent import MonitorPluginAgent
from sysinvest.common.bytesizes import shorthand2sizeof




class CheckFileAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj: dict ):
        super().__init__( parent, obj )
        self.__filename = obj.get( 'filename' )
        self.__minimal_size = obj.get( 'minimal_size' )
        if isinstance( self.__minimal_size, str ):
            self.__minimal_size = shorthand2sizeof( self.__minimal_size )

        self.__maximal_size = obj.get( 'maximal_size' )
        if isinstance( self.__maximal_size, str ):
            self.__maximal_size = shorthand2sizeof( self.__maximal_size )

        self.__expire = obj.get( 'expire' )
        if isinstance( self.__expire, str ):
            self.__expire = time2seconds( self.__expire )

        self.__mode = obj.get( 'mode' )
        return

    def execute( self ) -> TaskStatus:
        self.Status = TaskStatus.FAILED
        super().execute()
        data = FileExists( filename = self.__filename, exists = False,
                           size_valid = self.__minimal_size is None,
                           expired = self.__expire is not None )
        self.log.info( f"Checking: {self.__filename}" )
        if self.__filename is not None:
            self.log.info( f"Testing {self.__filename} for existance" )
            data.exists = os.path.exists( self.__filename )
            if data.exists:
                try:
                    stat_data = os.stat( self.__filename )
                    data.mode= stat.filemode( stat_data.st_mode )
                    data.ino= stat_data.st_ino
                    data.dev= stat_data.st_dev
                    data.nlink= stat_data.st_nlink
                    data.uid= stat_data.st_uid
                    data.gid = stat_data.st_gid
                    data.size = stat_data.st_size
                    data.atime = stat_data.st_atime
                    data.mtime = stat_data.st_mtime
                    data.ctime = stat_data.st_ctime
                    msg = []
                    msg.append( 'File exists' )
                    self.Status = TaskStatus.OK
                    if self.__mode is not None and self.__mode != data.mode:
                        msg.append( f"The file attributes '{data.mode}' are not '{self.__mode}'" )
                        self.Status = TaskStatus.FAILED

                    if self.__minimal_size is not None and self.__maximal_size is not None:
                        data.size_valid = stat_data.st_size >= self.__minimal_size and stat_data.st_size <= self.__maximal_size
                        if not data.size_valid:
                            msg.append( f"File size ({stat_data.st_size}) not between {self.__minimal_size} and {self.__maximal_size}" )
                            self.Status = TaskStatus.FAILED

                    else:
                        if self.__minimal_size is not None:
                            data.size_valid = stat_data.st_size >= self.__minimal_size
                            if not data.size_valid:
                                msg.append( f"File size too small ({stat_data.st_size}) must be atleast {self.__minimal_size}" )
                                self.Status = TaskStatus.FAILED

                        if self.__maximal_size is not None:
                            data.size_valid = stat_data.st_size <= self.__maximal_size
                            if not data.size_valid:
                                msg.append( f"File size too big ({stat_data.st_size}) must be less then {self.__maximal_size}" )
                                self.Status = TaskStatus.FAILED

                    if self.__expire is not None:
                        data.expired = ( stat_data.st_mtime + self.__expire ) < time.time()
                        if data.expired:
                            msg.append( f'File is expired, is older than { datetime.fromtimestamp( stat_data.st_mtime + self.__expire ) }' )
                            self.Status = TaskStatus.FAILED

                    self.Message = "\n".join( msg )
                    self.setServerData( data )

                except Exception as exc:
                    self.log.exception( "During lookup process" )
                    self.setExceptionData( exc, traceback.extract_stack() )

            else:
                self.Message = "Filename doesn't exist"

        else:
            self.Message = "Filename not configured"

        return self.Status
