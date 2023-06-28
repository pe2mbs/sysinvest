from typing import Union
import psutil
from threading import Thread
import time
import statistics

class CpuInfo( object ):
    def __init__( self ):
        return

    @property
    def cpu1min( self ):
        return 0

    @property
    def cpu5min( self ):
        return 0

    @property
    def cpu15min( self ):
        return 0


class MemInfo( object ):
    def __init__( self, mem: Union[ list, tuple ] ):
        self.__total        = mem[ 0 ]
        self.__available    = mem[ 1 ]
        self.__percent      = mem[ 2 ]
        return

    @property
    def Percent( self ):
        return self.__percent

    @property
    def Available( self ):
        return self.__available

    @property
    def Total( self ):
        return self.__total



class SystemLoads( Thread ):
    def __init__( self ):
        super().__init__()
        self.__cpuData = [ [] for i in range( len( psutil.cpu_percent( percpu = True ) ) ) ]
        self.__memData = []
        return

    def __getCpuAverages( self ):
        result = {}
        min1 = 0
        min5 = 0
        min15 = 0
        noCpus = len( self.__cpuData )
        for core, data in enumerate( self.__cpuData ):
            result.setdefault( core, {} )
            cnt = len( data )
            if cnt >= 12:
                load = statistics.mean( self.__cpuData[ core ][-13:] )
                min1 += load
                result[ core ][ '1 min' ] = load
                if cnt >= 60:
                    load = statistics.mean( self.__cpuData[ core ][ -61 : ] )
                    min5 += load
                    result[core]['5 min'] = load
                    if cnt >= 180:
                        load = statistics.mean( self.__cpuData[ core ] )
                        min15 += load
                        result[core]['15 min'] = load

                    else:
                        result[core]['15 min'] = 0

                else:
                    result[core]['5 min'] = 0
                    result[core]['15 min'] = 0

        result[ 'total' ] = {
            '1 min': min1 / noCpus,
            '5 min': min5 / noCpus,
            '15 min': min15 / noCpus
        }
        return result

    def run( self ):
        cnt = 0
        while True:
            start = time.time()
            for idx, cpu_pers in enumerate( psutil.cpu_percent(percpu=True) ):
                self.__cpuData[ idx ].append( cpu_pers )

            mem = psutil.virtual_memory()
            self.__memData.append( MemInfo( mem ) )
            time.sleep( 5 - ( time.time() - start ) )
            if len( self.__cpuData ) > (12 * 15):
                del self.__cpuData[ 0 ]
                del self.__memData[ 0 ]

            cnt += 1

        return

    def getLoadData( self ):
        if len( self.__memData ) > 0:
            return ( self.__memData[ -1 ], self.__getCpuAverages() )

        return ( None, None )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sysLoads = SystemLoads()
    sysLoads.run()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/