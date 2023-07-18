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
        self.__logger       = logging.getLogger( 'proxy' )
        self.__pac          = None
        self.__scheme       = None
        self.__hostname     = None
        self.__port         = 0
        self.__pacResolver  = None

        if isinstance( proxy, dict ):
            if 'pac' in proxy:
                self.__pac = proxy[ 'pac' ]
                self.__logger.info( f"Getting PAC data from: {self.__pac}")
                self.__pacResolver = get_pac( url = self.__pac, timeout = 10,
                                              allowed_content_types = [ 'application/octet-stream', "application/x-ns-proxy-autoconfig", "application/x-javascript-config" ]
                                              )
                self.__logger.info( f"PAC resolver {self.__pacResolver}" )

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
        if self.__pac is not None and self.__pacResolver is not None:
            scheme, host, _, _, _, _ = urllib.parse.urlparse(url)
            self.__logger.info( "Lookup URL {url} with hostname {host}".format( url = url, host = host ) )
            result = self.__pacResolver.find_proxy_for_url( url, host )
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

