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
from sysinvest.common.interfaces import TaskStatus, ServerLoadsData, OverallCpuLoadData, MemoryLoadData
from sysinvest.common.plugin_agent import MonitorPluginAgent
import sysinvest.common.api as API
from sysinvest.agent.plugins.serverloads.cpu import SystemLoads
from  datetime import datetime, timezone


class SystemLoadsAgent( MonitorPluginAgent ):
    DEFAULT_TEMPLATE = """${message}
Memory usage:    ${ round( memInfo.Percent, 2 ) }% 
CPU usage 1 min: ${ round( cpuInfo.get( "total", {} ).get( "1 min" ), 2 ) }% / 5 min: ${ round( cpuInfo.get( "total", {} ).get( "5 min" ), 2 ) }% / 15 min: ${ round( cpuInfo.get( "total", {} ).get( "15 min" ), 2 ) }%"""
    def __init__( self, parent, obj  ):
        super().__init__( parent, obj )
        self.__mem_threshold = obj.get( 'threshold', {} ).get( 'memory', 80 )
        self.__cpu_threshold_1_min = obj.get( 'threshold', {} ).get( 'cpu1min', 100 )
        self.__cpu_threshold_5_min = obj.get( 'threshold', {} ).get( 'cpu5min', 90 )
        self.__cpu_threshold_15_min = obj.get( 'threshold', {} ).get( 'cpu15min', 80 )
        self.__thread = SystemLoads()
        self.__thread.start()
        return

    def stop( self ):
        # Forward the stop to the thread
        self.__thread.stop()
        return

    def execute( self ) -> TaskStatus:
        super().execute()
        memInfo, cpuInfo = self.__thread.getLoadData()
        memInfo: MemoryLoadData
        cpuInfo: OverallCpuLoadData
        self.log.info( "Collecting Memory and CPU data" )
        if isinstance( memInfo, MemoryLoadData ) and isinstance( cpuInfo, OverallCpuLoadData ):
            messages = []
            memOk   = True
            cpuOk   = True
            if memInfo.percent >= self.__mem_threshold:
                messages.append( "Memory threshold exceeded" )
                memOk   = False

            if cpuInfo.minute_1_load >= self.__cpu_threshold_1_min:
                messages.append( "CPU: 1 minute threshold exceeded" )
                cpuOk = False

            if cpuInfo.minute_5_load >= self.__cpu_threshold_5_min:
                messages.append( "CPU: 5 minute threshold exceeded" )
                cpuOk = False

            if cpuInfo.minute_15_load >= self.__cpu_threshold_15_min:
                messages.append( "CPU: 15 minute threshold exceeded" )
                cpuOk = False

            if len( messages ) == 0:
                if len( cpuInfo.cores ) == 0:
                    messages.append( "Server loads collecting" )

                else:
                    messages.append( "Server loads normal" )

            self.Status = TaskStatus.OK
            self.setServerData( ServerLoadsData( cpu = cpuOk, mem = memOk,
                                                 messages = messages,
                                                 cpuLoad = cpuInfo,
                                                 memload = memInfo,
                                                 since = self.Since,
                                                 tasks = self.Parent.TaskCount,
                                                 lasttime = datetime.utcnow().replace( tzinfo = timezone.utc ) ) )

        else:
            self.Status = TaskStatus.COLLECTING
            self.setServerData( None )

        return self.Status

