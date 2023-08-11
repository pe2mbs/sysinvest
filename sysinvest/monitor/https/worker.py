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
import os
from sysinvest.common.plugin import MonitorPlugin
import traceback
import sysinvest.common.plugin.constants as const
import sysinvest.monitor.http.requester as req
import sysinvest.common.api as API
import certifi


def checkCertKey( cert, key, result ):
    if not os.path.isfile( cert ):
        result.Result = False
        result.Message = "'cert[ 0 ]' (cert) {cert} is NOT a file"

    elif not os.path.exists( cert ):
        result.Result = False
        result.Message = "'cert[ 0 ]' (cert) {cert} is NOT existing file"

    elif not cert.lower().endswith( '.pem' ):
        result.Result = False
        result.Message = "'cert[ 0 ]' (cert) {cert} is NOT a PEM file"

    if result.Result:
        if not os.path.isfile( key ):
            result.Result = False
            result.Message = "'cert[ 1 ]' (key) {key} is NOT a file"

        elif not os.path.exists( key ):
            result.Result = False
            result.Message = "'cert[ 1 ]' (key) {key} is NOT existing file"

        elif not key.lower().endswith( '.pem' ):
            result.Result = False
            result.Message = "'cert[ 1 ]' (key) {key} is NOT a PEM file"

    return result.Result


class Https( MonitorPlugin ):
    def execute( self ):
        super().execute()
        kwargs = self.Attributes.get( 'parameters', {} )
        self.log.debug( f"CA certifcates: {certifi.where()}" )
        if 'username' in kwargs:
            # JNeed to translate the username/password
            auth = ( kwargs[ 'username' ], kwargs[ 'password' ] )
            del kwargs[ 'username' ]
            del kwargs[ 'password' ]
            kwargs[ 'auth' ] = auth

        # We need to deal with CA, cert or keysfiles
        # :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        # :param verify: (optional) Either a boolean, in which case it controls whether we verify
        #                           the server's TLS certificate, or a string, in which case it must be a path
        #                           to a CA bundle to use. Defaults to ``True``.
        self.update(True, "")
        verify = kwargs.get( 'verify', certifi.where() )
        if isinstance( verify, bool ):
            pass

        elif isinstance( verify, str ):
            if not os.path.isfile( verify ):
                self.update( False, "'verify' {verify} is NOT a file" )

            elif not os.path.exists( verify ):
                self.update( False, "'verify' {verify} is NOT existing file" )

        elif verify is not None:
            self.update( False, "Invalid 'verify' parameter" )

        if not self.Result:
            return

        verify = kwargs.get( 'cert' )
        if isinstance( verify, str ):
            if not os.path.isfile( verify ):
                self.update( False, "'cert' {verify} is NOT a file" )

            elif not os.path.exists( verify ):
                self.update( False, "'cert' {verify} is NOT existing file" )

        elif isinstance( verify, (tuple,list) ) and len( verify ) == 2:
            if checkCertKey( *verify, result = self ):
                # Make sure that 'cert' is a tuple
                kwargs[ 'cert' ] = tuple( verify )

        elif isinstance( verify, dict ):
            if checkCertKey( verify.get( 'cert' ), verify.get( 'key' ), self ):
                # Make sure that 'cert' is a tuple
                kwargs[ 'cert' ] = ( verify.get( 'cert' ), verify.get( 'key' ) )

        elif verify is not None:
            self.update( False, "Invalid 'cert' parameter" )

        if self.Result:
            url = self.Attributes.get( 'url', 'https://localhost' )
            if req.requests is not None:
                try:
                    result = req.doRequest( self, url, **kwargs )

                except Exception as exc:
                    self.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() },
                                           filename = url )
            else:
                self.update( False, "Python 'requests' package not installed",
                                       { const.C_EXCEPTION: "ModuleNotFoundError: No module named 'requests'",
                                         const.C_TRACEBACK: traceback.format_stack() },
                                       filename = url )

        API.QUEUE.put( self )
        return
