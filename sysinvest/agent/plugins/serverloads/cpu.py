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
from typing import Union
import psutil
from threading import Thread, Event, RLock
import time
import statistics
from sysinvest.common.interfaces import MemoryLoadData, CpuLoadData, OverallCpuLoadData


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

    def interface( self ) -> MemoryLoadData:
        return MemoryLoadData( total = self.__total, available = self.__available, percent = self.__percent )


class SystemLoads( Thread ):
    def __init__( self ):
        super().__init__()
        self.__event = Event()
        self.__lock = RLock()
        self.__cpuData = [ [] for i in range( len( psutil.cpu_percent( percpu = True ) ) ) ]
        self.__memData = []
        return

    def __getCpuAverages( self ):
        cores = []
        total_min1 = 0
        total_min5 = 0
        total_min15 = 0
        noCpus = len( self.__cpuData )
        for core, data in enumerate( self.__cpuData ):
            cnt = len( data )
            if cnt >= 12:
                min1 = statistics.mean( self.__cpuData[ core ][-13:] )
                total_min1 += min1
                if cnt >= 60:
                    min5 = statistics.mean( self.__cpuData[ core ][ -61 : ] )
                    total_min5 += min5
                    if cnt >= 180:
                        min15 = statistics.mean( self.__cpuData[ core ] )
                        total_min15 += min15

                    else:
                        min15 = 0

                else:
                    min5 = 0
                    min15 = 0

                cores.append( CpuLoadData( core = core, minute_1_load = min1, minute_5_load = min5, minute_15_load = min15 ) )

        return OverallCpuLoadData( minute_1_load = total_min1 / noCpus,
                                   minute_5_load = total_min5 / noCpus,
                                   minute_15_load = total_min15 / noCpus,
                                   cores = cores )

    def stop( self ):
        self.__event.set()
        self.join()
        return

    def run( self ):
        cnt = 0
        while not self.__event.is_set():
            start = time.time()
            self.__lock.acquire()
            for idx, cpu_pers in enumerate( psutil.cpu_percent(percpu=True) ):
                self.__cpuData[ idx ].append( cpu_pers )

            self.__lock.release()
            mem = psutil.virtual_memory()
            self.__memData.append( MemInfo( mem ) )
            self.__event.wait( 5 - ( time.time() - start ) )
            if len( self.__cpuData ) > (12 * 15):
                self.__lock.acquire()
                del self.__cpuData[ 0 ]
                del self.__memData[ 0 ]
                self.__lock.release()

            cnt += 1

        return

    def getLoadData( self ):
        result = (None, None)
        if len( self.__memData ) > 0:
            self.__lock.acquire()
            try:
                result = ( self.__memData[ -1 ].interface(), self.__getCpuAverages() )

            except:
                pass

            finally:
                self.__lock.release()

        return result

    def interface( self ) -> OverallCpuLoadData:
        self.__lock.acquire()
        try:
            return self.__getCpuAverages()

        except:
            pass

        finally:
            self.__lock.release()

        return None
