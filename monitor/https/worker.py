import os
from common.plugin import MonitorPlugin, PluginResult
import traceback
import common.plugin.constants as const
import monitor.http.requester as req


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
        task_result = PluginResult( self )
        kwargs = self.Attributes.get( 'parameters', {} )
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
        verify = kwargs.get( 'verify' )
        if isinstance( verify, bool ):
            pass

        elif isinstance( verify, str ):
            if not os.path.isfile( verify ):
                task_result.update( False, "'verify' {verify} is NOT a file" )

            elif not os.path.exists( verify ):
                task_result.update( False, "'verify' {verify} is NOT existing file" )

        elif verify is not None:
            task_result.update( False, "Invalid 'verify' parameter" )

        if not task_result.Result:
            return

        verify = kwargs.get( 'cert' )
        if isinstance( verify, str ):
            if not os.path.isfile( verify ):
                task_result.update( False, "'cert' {verify} is NOT a file" )

            elif not os.path.exists( verify ):
                task_result.update( False, "'cert' {verify} is NOT existing file" )

        elif isinstance( verify, (tuple,list) ) and len( verify ) == 2:
            if checkCertKey( *verify, result = task_result ):
                # Make sure that 'cert' is a tuple
                kwargs[ 'cert' ] = tuple( verify )

        elif isinstance( verify, dict ):
            if checkCertKey( verify.get( 'cert' ), verify.get( 'key' ), task_result ):
                # Make sure that 'cert' is a tuple
                kwargs[ 'cert' ] = ( verify.get( 'cert' ), verify.get( 'key' ) )

        elif verify is not None:
            task_result.update( False, "Invalid 'cert' parameter" )

        if task_result.Result:
            url = self.Attributes.get( 'url', 'https://localhost' )
            if req.requests is not None:
                try:
                    result = req.doRequest( self, url, **kwargs )

                except Exception as exc:
                    task_result.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() },
                                           filename = url )
            else:
                task_result.update( False, "Python 'requests' package not installed",
                                       { const.C_EXCEPTION: "ModuleNotFoundError: No module named 'requests'",
                                         const.C_TRACEBACK: traceback.format_stack() },
                                       filename = url )

        self.Monitor.Queue.put( task_result )
        return
