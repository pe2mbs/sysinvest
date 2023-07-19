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
from typing import List, Union, Optional
import psutil
import time
import statistics
from threading import Event, Thread, RLock
from sysinvest.common.bytesizes import sizeof2shorthand, shorthand2sizeof


class NetworkData( object ):
    def __init__( self, intf: Optional[Union[str,'NetworkData']] = None,
                  rx: Optional[int] = None, tx: Optional[int] = None,
                  rxs: Optional[int] = None, txs: Optional[int] = None, delay: Optional[Union[int,float]] = 1 ):
        if isinstance( intf, NetworkData ):
            self.__interface = intf.__interface
            self.__rxBytes  = intf.__rxBytes
            self.__txBytes  = intf.__txBytes
            self.__rxSpeed  = intf.__rxSpeed
            self.__txSpeed  = intf.__txSpeed
            self.__update_delay = intf.__update_delay
            return

        self.__interface = intf
        self.__rxBytes  = None
        self.__txBytes  = None
        self.__rxSpeed  = None
        self.__txSpeed  = None
        self.__avgRxSpeed  = None
        self.__avgTxSpeed  = None
        self.__update_delay = delay
        if intf is not None:
            self.set( rx, tx, rxs, txs )

        return

    def set( self, rx: int, tx: int, rxs: int, txs: int ) -> None:
        self.__rxBytes  = rx
        self.__txBytes  = tx
        self.__rxSpeed  = rxs
        self.__txSpeed  = txs
        return

    def dump( self ) -> None:
        print( f"iface: { self.__interface }" )
        print( f"  Download:       { sizeof2shorthand( self.__rxBytes ) }" )
        print( f"  Upload:         { sizeof2shorthand( self.__txBytes ) }" )
        print( f"  Upload Speed:   { sizeof2shorthand( self.__rxSpeed / self.__update_delay ) }/s" )
        print( f"  Download Speed: { sizeof2shorthand( self.__txSpeed / self.__update_delay ) }/s" )
        return

    @property
    def Interface( self ) -> str:
        return self.__interface

    @property
    def ReceiveBytes( self ) -> int:
        return self.__rxBytes

    @property
    def TransmitBytes( self ) -> int:
        return self.__txBytes

    @property
    def ReceiveSpeed( self ) -> int:
        return self.__rxSpeed

    @property
    def TransmitSpeed( self ) -> int:
        return self.__txSpeed

    @property
    def AverageReceiveSpeed( self ) -> int:
        return self.__avgRxSpeed

    @property
    def AverageTransmitSpeed( self ) -> int:
        return self.__avgTxSpeed

    def setAverage( self, rx, tx ):
        self.__avgRxSpeed  = int(rx)
        self.__avgTxSpeed  = int(tx)
        return


class FoundNetworkItem( Exception ):
    def __init__( self, data: NetworkData ):
        super().__init__( data.Interface )
        self.data = data
        return


class NetworkInfo( Thread ):
    def __init__( self, interval: Optional[Union[int,float]] = 1 ):
        super().__init__()
        self.__list = []
        self.__interval = interval
        self.__event = Event()
        self.__lock = RLock()
        self.__history = {}
        return

    def stop( self ) -> None:
        self.__event.set()
        return

    def dump( self, iface: Optional[str] = None ) -> None:
        for item in self.__list:
            if iface is None:
                item.dump()

            elif iface == item.Interface:
                item.dump()
                break

        return

    def __update( self, iface: str, bytes_recv: int, bytes_sent: int, upload_speed: int, download_speed: int, update_delay: int ) -> None:
        self.__lock.acquire()
        item = None
        try:
            for item in self.__list:
                if item.Interface == iface:
                    raise FoundNetworkItem( item )

            # Not found, so we add it
            item = NetworkData( iface, bytes_recv, bytes_sent, upload_speed, download_speed, update_delay )
            self.__list.append( item )

        except FoundNetworkItem as data:
            # Update the existing item
            item = data.data
            item.set( bytes_recv, bytes_sent, upload_speed, download_speed )

        finally:
            if isinstance( item, NetworkData ):
                # Add it to the history per adaptor
                self.__history.setdefault( iface, [] ).append( NetworkData( item ) )

            # Check that the history contains NO more that a minute of data
            for iface in list( self.__history.keys() ):
                if len( self.__history[ iface ] ) > int( 60 / self.__interval ):
                    del self.__history[ iface ][ 0 ]

            self.__lock.release()

        return

    def run( self ) -> None:
        st = time.time()
        measure_nic_start = psutil.net_io_counters( pernic = True )
        measure_total_start = psutil.net_io_counters()
        while not self.__event.is_set():
            # Calculate the time we need to sleep to be at 'interval'
            sleep = self.__interval - ( time.time() - st )
            self.__event.wait( sleep )
            st = time.time()

            # get the network I/O stats again per interface
            measure_nic_end = psutil.net_io_counters( pernic = True )
            measure_total_end = psutil.net_io_counters()
            # initialize the data to gather (a list of dicts)
            for ( iface, iface_start ), ( iface2, iface_end ) in zip( measure_nic_start.items(), measure_nic_end.items() ):
                # start - end stats gets us the speed
                self.__update( iface, iface_end.bytes_recv, iface_end.bytes_sent,
                               iface_end.bytes_sent - iface_start.bytes_sent,
                               iface_end.bytes_recv - iface_start.bytes_recv, self.__interval )

            # start - end stats gets us the speed
            self.__update( 'Total', measure_total_end.bytes_recv, measure_total_end.bytes_sent,
                           measure_total_end.bytes_sent - measure_total_start.bytes_sent,
                           measure_total_end.bytes_recv - measure_total_start.bytes_recv,
                           self.__interval )

            # update the I/O stats for the next iteration
            measure_nic_start = measure_nic_end
            measure_total_start = measure_total_end

        self.__event.clear()
        return

    def getLoadData( self ) -> List[NetworkData]:
        data = []
        self.__lock.acquire()
        try:
            averages = {}
            # Calculate the average speeds for all interfaces
            for iface, history in self.__history.items():
                hist: NetworkData
                rxSpeed = [ hist.ReceiveSpeed for hist in history if isinstance( hist.ReceiveSpeed, int ) ]
                txSpeed = [ hist.TransmitSpeed for hist in history if isinstance( hist.TransmitSpeed, int ) ]
                averages[ iface ] = ( statistics.mean( rxSpeed ), statistics.mean( txSpeed ) )

            for item in self.__list:
                # Copy the interface data and add the average speeds
                newItem = NetworkData( item )
                newItem.setAverage( *averages[ item.Interface ] )
                data.append( newItem )

        finally:
            self.__lock.release()

        return data
