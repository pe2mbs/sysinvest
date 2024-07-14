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
import traceback
import psutil
from datetime import datetime, timezone
from sysinvest.common.checkpid import updateProcessData
from sysinvest.common.interfaces import TaskStatus, ExceptionData, ProcessData
from sysinvest.common.plugin_agent import MonitorPluginAgent
import sysinvest.common.api as API


class CheckProcessAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj: dict ):
        super().__init__( parent, obj )
        self.__executable = obj.get( 'executable' )
        self.__commandline = obj.get( 'commandline', [ ] )
        if isinstance( self.__commandline, str ):
            self.__commandline = self.__commandline.split( ' ' )

        self.__serverData = ProcessData( pid = 0,
                                         since = datetime.utcnow().replace( tzinfo = timezone.utc ),
                                         lasttime = datetime.utcnow().replace( tzinfo = timezone.utc ),
                                         tasks = parent.TaskCount )
        return

    def execute( self ) -> TaskStatus:
        super().execute()
        self.setServerData( self.__serverData )
        self.Status = TaskStatus.FAILED
        try:
            for proc in psutil.process_iter():
                try:
                    cmdline = proc.cmdline()
                    # self.log.info( "Process {}".format( " ".join( cmdline ) ) )
                    if len( cmdline ) > 0 and cmdline[0] == self.__executable:
                        self.log.debug( f"executable found: {self.__executable} ")
                        count = 0
                        for arg in self.__commandline:
                            if arg in cmdline[1:]:
                                count += 1

                        if count == len(self.__commandline):
                            updateProcessData( proc, self.__serverData )
                            self.Status = TaskStatus.OK
                            break

                except psutil.AccessDenied:
                    pass

                except Exception:
                    raise

            result = ' '.join( self.__commandline )
            if self.Status == TaskStatus.FAILED:
                self.log.warning( f"process NOT found: { self.__executable } {result}" )
                self.setServerData( None )  # Clear the server data
                self.Message = f"Executable { self.__executable } with command line '{result}' doesn't exist"

            else:
                self.setServerData( self.__serverData )
                self.Message = f"Executable { self.__executable } with command line '{result}' exist"

        except Exception as exc:
            self.log.exception( "During lookup process" )
            self.Status = TaskStatus.FAILED
            self.setExceptionData( exc, traceback.extract_stack() )

        return self.Status
