from sysinvest.common.plugin import MonitorPlugin, PluginResult
import traceback
import sysinvest.common.plugin.constants as const
import sysinvest.monitor.http.requester as req
import sysinvest.common.api as API


class Http( MonitorPlugin ):
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

        url = self.Attributes.get( 'url', 'http://localhost' )
        if req.requests is not None:
            try:
                req.doRequest( self, task_result, url, **kwargs )

            except Exception as exc:
                task_result.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() },
                                       filename = url )

        else:
            task_result.update( False, "Python 'requests' package not installed",
                                   { const.C_EXCEPTION: "ModuleNotFoundError: No module named 'requests'",
                                     const.C_TRACEBACK: traceback.format_stack() },
                                   filename = url )

        API.QUEUE.put( task_result )
        return