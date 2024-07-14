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
from sysinvest.common.interfaces import ProcessData, ExceptionData, TaskStatus
from sysinvest.common.plugin_agent import MonitorPluginAgent
import sysinvest.common.constants as const
from sysinvest.common.checkpid import checkPidFilename, updateProcessData
from datetime import datetime, timezone


class ValidStatus( Exception ):
    def __init__( self, process ):
        self.process = process
        return


class CheckPidAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj: dict ):
        super().__init__( parent, obj )
        self.__pid = obj.get( const.C_PID, 0 )
        self.__filename = obj.get( const.C_FILENAME )
        self.__executable = obj.get( 'executable' )
        self.__commandline = obj.get( 'commandline' )
        if isinstance( self.__commandline, str ):
            self.__commandline = self.__commandline.split( ' ' )

        self.__serverData = ProcessData( pid = 0,
                                         since = datetime.utcnow().replace(tzinfo = timezone.utc),
                                         lasttime = datetime.utcnow().replace(tzinfo = timezone.utc),
                                         tasks = parent.TaskCount )
        self.runOnStartup()
        return
    def execute( self ) -> TaskStatus:
        super().execute()
        self.Status = TaskStatus.FAILED
        try:
            self.log.info( f"Checking PID file: {self.__filename}")
            if isinstance( self.__filename, str ):
                if not os.path.exists( self.__filename ):
                    raise ProcessLookupError( "PID filename doesn't exist" )

            else:
                raise ProcessLookupError( "PID filename not configured" )

            # now check if the PID exists
            result, self.__pid = checkPidFilename( self.__filename )
            if not result:
                raise ProcessLookupError( f"process with PID {self.__pid} does not exist for PID file {self.__filename}" )

            if not isinstance( self.serverData, ProcessData ):
                self.setServerData( self.__serverData )

            process = psutil.Process( self.__pid )
            self.serverData.pid = self.__pid
            if not isinstance( self.__executable, str ):
                raise ValidStatus( process )

            cmdline = process.cmdline()
            if cmdline[ 0 ] != self.__executable:
                raise ProcessLookupError( "Executable not the same as configured" )

            if not isinstance( self.__commandline, ( list, tuple ) ):
                raise ValidStatus( process )

            msg = []
            for cmd in self.__commandline:
                if cmd not in cmdline:
                    msg.append( f"{cmd} not found in command line" )

            if len( msg ) == 0:
                cmdline = ' '.join(cmdline)
                self.Message = f"process exists: {cmdline} with PID {self.__pid}"
                raise ValidStatus( process )

            cmdline = ' '.join(cmdline)
            raise ProcessLookupError( f"process exists, but has invalid executable line: {cmdline}" )

        except ValidStatus as exc:
            self.setServerData( self.__serverData )
            self.Status = TaskStatus.OK
            if self.Message == '':
                self.Message = f"process exists"

            updateProcessData( exc.process, self.serverData )

        except psutil.NoSuchProcess:
            self.setServerData( None )  # Clear the server data
            self.Message = f"The process with PID {self.__pid} doesn't esists"

        except ProcessLookupError as exc:
            self.setServerData( None )  # Clear the server data
            self.Message = str( exc )

        except Exception as exc:
            stack = traceback.format_exc().split('\n')
            self.setExceptionData( exc, traceback.extract_stack() )

        return self.Status
