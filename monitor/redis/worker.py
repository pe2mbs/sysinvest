import traceback
import common.plugin.constants as const
from common.plugin import MonitorPlugin, PluginResult
import common.api as API
try:
    import redis

except:
    redis = None


class RedisMonitor( MonitorPlugin ):
    def execute( self ):
        url = self.Attributes.get( 'url' )
        task_result = PluginResult( self )
        if redis is not None and url is not None:
            redis.Redis.from_url( url )
            task_result.update( True, "" )

        else:
            task_result.update( False, "Python 'redis' package not installed",
                                   { const.C_EXCEPTION: "ModuleNotFoundError: No module named 'redis'",
                                     const.C_TRACEBACK: traceback.format_stack() },
                                   filename = url )

        API.QUEUE.put( task_result )
        return