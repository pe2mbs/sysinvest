from sysinvest.common.plugin import MonitorPlugin
import sysinvest.common.api as API
from sysinvest.monitor.network.networkstats import NetworkData, NetworkInfo
from sysinvest.common.bytesizes import sizeof2shorthand, shorthand2sizeof
import socket


class NetworkMonitor( MonitorPlugin ):
    DEFAULT_TEMPLATE = """${message}
"""
    def __init__( self, parent, obj  ):
        super().__init__( parent, obj )
        self.__thread = NetworkInfo( interval = 5 )
        self.__thread.start()
        return

    def stop( self ):
        # Forward the stop to the thread
        self.__thread.stop()
        return

    def execute( self ):
        netInfo = self.__thread.getLoadData()
        if isinstance( netInfo, list ) and len( netInfo ) > 0:
            messages = []
            errors = []
            netOk   = True
            interfaces = self.Attributes.get( 'interfaces', [] )
            for interface in interfaces:
                iface       = interface.get( 'interface' )
                address     = interface.get( 'address' )
                hostname    = interface.get( 'hostname' )

                if address is not None and hostname is not None:
                    if socket.getfqdn( address ) != hostname:
                        errors.append( f"{iface} has a WRONG IP address {address}/hostname {socket.getfqdn( address )} should be {hostname}")
                        netOk   = False

                media = interface.get( 'media' )
                threshold = interface.get( 'threshold' )
                if media is not None and threshold is not None:
                    if isinstance( media, (int,str) ):
                        media = shorthand2sizeof( media )

                    max_media = media * (threshold/100)
                    for net in netInfo:
                        if net.Interface == iface:
                            if net.ReceiveSpeed > max_media:
                                errors.append( f"the rx-Speed exceeds the threshold: {net.ReceiveSpeed} >= {threshold}%" )
                                netOk   = False

                            if net.TransmitSpeed > max_media:
                                errors.append( f"the tx-Speed exceeds the threshold: {net.TransmitSpeed} >= {threshold}%" )
                                netOk   = False

                            messages.append( f"{iface} Received: {net.ReceiveBytes}  Transmitted: {net.TransmitBytes}  Rx-Speed: {net.AverageReceiveSpeed}  Tx-Speed: {net.AverageTransmitSpeed}" )

            if len( messages ) == 0:
                messages.append( "Network loads normal" )

            if netOk:
                self.update( netOk, '\n'.join( messages ), netInfo = netInfo )

            else:
                self.update( netOk, "{}\n{}".format( '\n'.join( errors ), '\n'.join( messages ) ), netInfo = netInfo )

        else:
            self.update( True, "Collecting", memInfo = [] )

        API.QUEUE.put( self )
        return

