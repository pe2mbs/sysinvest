from common.plugin import MonitorPlugin, PluginResult
import common.api as API
from monitor.serverloads.cpu import SystemLoads

class ServerLoads( MonitorPlugin ):
    DEFAULT_TEMPLATE = """${message}
Memory usage:     ${ memInfo.get( "present", None ) }
CPU usage 1 min:  ${ cpuInfo.get( "total", {} ).get( "1 min" ) } / 5 min:  ${ cpuInfo.get( "total", {} ).get( "5 min" ) } / 15 min: ${ cpuInfo.get( "total", {} ).get( "15 min" ) }"""
    def __init__( self, parent, obj  ):
        super().__init__( parent, obj )
        self.__mem_threshold = 80
        self.__cpu_threshold_1_min = 100
        self.__cpu_threshold_5_min = 90
        self.__cpu_threshold_15_min = 80
        self.__thread = SystemLoads()
        self.__thread.start()
        return

    def execute( self ):
        task_result = PluginResult( self )
        memInfo, cpuInfo = self.__thread.getLoadData()
        if isinstance( memInfo, dict ):
            messages = []
            memOk   = True
            cpuOk   = True
            if memInfo[ 'percent' ] >= self.__mem_threshold:
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
            task_result.update( True, "Collecting", memInfo = {}, cpuInfo = {} )

        API.QUEUE.put( task_result )
        return

