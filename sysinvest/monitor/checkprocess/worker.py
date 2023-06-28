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
from sysinvest.common.plugin import MonitorPlugin, PluginResult
import sysinvest.common.plugin.constants as const
import copy
import psutil
from sysinvest.common.checkpid import checkPidFilename
import sysinvest.common.api as API

class CheckProcess( MonitorPlugin ):
    def execute( self ) -> None:
        super().execute()
        task_result = PluginResult( self )
        try:
            result = None
            processName = self.Attributes.get( const.C_NAME )
            listOfProcessObjects = []
            processAttrs = self.Attributes.get( const.C_INFO, [ const.C_PID, const.C_NAME, const.C_CREATE_TIME ] )
            commandline = self.Attributes.get( const.C_COMMANDLINE )
            if commandline is not None:
                if const.C_COMMANDLINE not in processAttrs:
                    processAttrs.append( const.C_COMMANDLINE )

            pidfile = self.Attributes.get( const.C_PID_FILE )
            if pidfile is not None:
                if os.path.exists( pidfile ):
                    result, pid = checkPidFilename( pidfile )
                    # now check if the PID exists
                    if not result:
                        task_result.update( False, f"a process with pid {pid} does not exist" )

                else:
                    task_result.update( False, f"PID filename {pidfile} doesn't exist" )

            if isinstance( result, PluginResult ):
                return result

            thresholds = self.Attributes.get( const.C_THRESHOLDS )
            if thresholds is not None:
                for key in thresholds.keys():
                    if key not in processAttrs:
                        processAttrs.append( key )

            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict( processAttrs )
                    # # Check if process name contains the given name string.
                    if processName in pinfo[ const.C_NAME ] and commandline == pinfo[ const.C_COMMANDLINE ][ 1: ]:
                        listOfProcessObjects.append( pinfo )

                except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
                    pass

            if len( listOfProcessObjects ) == 0:
                task_result.update( self, False, f"Process: {processName} doesn't exist" )

            else:
                if thresholds is None:
                    task_result.update( self, True, f"Process: {processName} active", { 'processes': listOfProcessObjects } )

                else:
                    data = copy.copy(thresholds)
                    for key in thresholds.keys():
                        data[ key ] = 0

                    for item in listOfProcessObjects:
                        for key, value in thresholds.items():
                            data[ key ] += item[ key ]

                    result = None
                    for tkey, tvalue in thresholds.items():
                        if data[ tkey ] > tvalue:
                            # Exceeding the threshold
                            task_result.update( self, False,
                                                   f"Process: {processName} active, but exceeds the {tkey} threshold {tvalue} with {data[ tkey ]}",
                                                   { 'processes': listOfProcessObjects } )
                            break

                    if result is None:
                        task_result.update( True, f"Process: {processName} active", { 'processes': listOfProcessObjects } )

        except Exception as exc:
            task_result.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() } )

        API.QUEUE.put( task_result )
        return
