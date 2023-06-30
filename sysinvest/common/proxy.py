import logging
import urllib.parse
try:
    from pypac import get_pac

except ModuleNotFoundError:
    get_pac = None

import urllib3
urllib3.disable_warnings()


class ProxyMixin( object ):
    def __init__( self, proxy = None, **kwargs ):
        self.__logger   = logging.getLogger( 'proxy' )
        self.__pac      = None
        self.__scheme   = None
        self.__hostname = None
        self.__port     = 0

        if isinstance( proxy, dict ):
            if 'pac' in proxy:
                self.__pac = proxy[ 'pac' ]

            elif 'scheme' in proxy:
                self.__scheme = proxy[ 'scheme' ]
                self.__hostname = proxy[ 'hostname' ]
                self.__port = proxy[ 'port' ]

            elif 'host' in proxy:
                self.__scheme, host, _, _, _, _ = urllib.parse.urlparse( proxy[ 'host' ] )
                self.__hostname, self.__port = host.split( ':' )

        elif isinstance( proxy, str ):
            if proxy.endswith( '.pac' ):
                self.__pac = proxy

            else:
                self.__scheme, host, _, _, _, _ = urllib.parse.urlparse( proxy )
                # test of ernst
                # self.__hostname, self.__port = host.split( ':' )
                self.__hostname, self.__port = proxy.split( ':' )

        return

    def resolveViaProxy( self, url ):
        proxyAddr = None
        if self.__pac is not None and callable( get_pac ):
            scheme, host, _, _, _, _ = urllib.parse.urlparse(url)
            self.__logger.info("Getting PAC data from: {url}".format(url=self.__pac))
            pac = get_pac( url = self.__pac )

            self.__logger.info( "Lookup URL {url} with hostname {host}".format( url = url, host = host ) )
            result = pac.find_proxy_for_url( url, host )
            self.__logger.info( 'Lookup result "{}"'.format( result ) )
            if result.startswith( 'PROXY ' ):
                name, proxyAddr = result.split( ' ' )

        elif self.__scheme is not None:
            proxyAddr = "{}:{}".format( self.__hostname, self.__port )

        elif self.__pac is not None and not callable( get_pac ):
            self.__logger.error( 'pypac package is not installed' )

        if proxyAddr is not None:
            result = { "http": "http://{}".format( proxyAddr ), "https": "http://{}".format( proxyAddr ) }
            self.__logger.info( "Using HTTP(S) proxy: {http} ({https})".format( **result ) )

            return result

        return None

