import socket
from sysinvest.common.interfaces import TaskStatus, NetworkInterface
from sysinvest.common.plugin_agent import MonitorPluginAgent
from sysinvest.agent.plugins.network.networkstats import NetworkInfo
from sysinvest.common.bytesizes import shorthand2sizeof



class NetworkMonitor( MonitorPluginAgent ):
    def __init__( self, parent, obj  ):
        super().__init__( parent, obj )
        self.Status = TaskStatus.COLLECTING
        self.__interfaces = [ NetworkInterface( **intf )  for intf in obj.get( 'interfaces', [] ) ]
        self.__thread = NetworkInfo( interval = 5 )
        self.__thread.start()
        return

    def stop( self ):
        # Forward the stop to the thread
        self.__thread.stop()
        return

    def execute( self ) -> TaskStatus:
        netInfo = self.__thread.getLoadData()
        if isinstance( netInfo, list ) and len( netInfo ) > 0:
            messages = []
            errors = []
            netOk   = True
            result  = []
            for intf in self.__interfaces:
                if intf.address is not None and intf.hostname is not None:
                    if socket.getfqdn( intf.address ) != intf.hostname:
                        errors.append( f"{intf.interface} has a wrong IP address {intf.address}/hostname {socket.getfqdn( intf.address )} should be {intf.hostname}")
                        netOk   = False

                if intf.media is not None and intf.threshold is not None:
                    if isinstance( intf.media, (int,str) ):
                        intf.media = shorthand2sizeof( intf.media )

                    max_media = intf.media * (intf.threshold/100)
                    for net in netInfo:
                        if intf.interface == net.Interface:
                            result.append( net )

                        if max_media > 0.0:
                            if net.Interface == intf.interface:
                                if net.ReceiveSpeed > max_media:
                                    errors.append( f"the rx-Speed exceeds the threshold: {net.ReceiveSpeed} >= {intf.threshold}%" )
                                    netOk   = False

                                if net.TransmitSpeed > max_media:
                                    errors.append( f"the tx-Speed exceeds the threshold: {net.TransmitSpeed} >= {intf.threshold}%" )
                                    netOk   = False

            self.setServerData( result )
            if len( messages ) == 0:
                messages.append( "Network loads normal" )

            if netOk:
                self.Message = '\n'.join( messages )
                self.Status = TaskStatus.OK

            else:
                self.Message = "{}\n{}".format( '\n'.join( errors ), '\n'.join( messages ) )
                self.Status = TaskStatus.FAILED

        else:
            self.Status = TaskStatus.COLLECTING
            self.Message = "Collecting"

        return self.Status

