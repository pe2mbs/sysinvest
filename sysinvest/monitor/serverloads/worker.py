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
from sysinvest.common.plugin import MonitorPlugin, PluginResult
import sysinvest.common.api as API
from sysinvest.monitor.serverloads.cpu import SystemLoads, MemInfo, CpuInfo


class ServerLoads( MonitorPlugin ):
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

    def execute( self ) -> bool:
        super().execute()
        task_result = PluginResult( self )
        memInfo, cpuInfo = self.__thread.getLoadData()
        self.log.info( "Collecting Memory and CPU data" )
        if isinstance( memInfo, MemInfo ):
            messages = []
            memOk   = True
            cpuOk   = True
            if memInfo.Percent >= self.__mem_threshold:
                messages.append( "Memory threshold exceeded" )
                memOk   = False

            cpuTotal = cpuInfo.get( 'total', {} )
            if cpuTotal.get( '1 min' ) >= self.__cpu_threshold_1_min:
                messages.append( "CPU: 1 minute threshold exceeded" )
                cpuOk = False

            if cpuTotal.get( '5 min' ) >= self.__cpu_threshold_5_min:
                messages.append( "CPU: 5 minute threshold exceeded" )
                cpuOk = False

            if cpuTotal.get( '15 min' ) >= self.__cpu_threshold_15_min:
                messages.append( "CPU: 15 minute threshold exceeded" )
                cpuOk = False

            if len( messages ) == 0:
                messages.append( "Server loads normal" )

            task_result.update( memOk and cpuOk, '\n'.join( messages ), memOk = memOk, cpuOk = cpuOk, memInfo = memInfo, cpuInfo = cpuInfo )

        else:
            task_result.update( True, "Collecting", memInfo = memInfo((0,0,0)), cpuInfo = {} )

        API.QUEUE.put( task_result )
        return task_result.Result

