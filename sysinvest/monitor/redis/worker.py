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
import traceback
import time
import uuid
from mako.template import Template
import sysinvest.common.plugin.constants as const
from sysinvest.common.plugin import MonitorPlugin, PluginResult
import sysinvest.common.api as API
try:
    import redis

except ModuleNotFoundError:
    redis = None


class RedisMonitor( MonitorPlugin ):
    DEFAULT_TEMPLATE = """${message}
"""
    def __init__( self, parent, obj ):
        super().__init__( parent, obj )
        self.__counter = 0
        self.__token = Template(self.Attributes.get('token')).render(uuid=uuid)
        return

    def execute( self ):
        username    = self.Attributes.get( 'username', None )
        passwd      = self.Attributes.get( 'password' )
        host        = self.Attributes.get( 'host', 'localhost' )
        ssl         = self.Attributes.get( 'ssl', False )
        port        = self.Attributes.get( 'port', 6379 if not ssl else 6666 )
        database    = self.Attributes.get( 'database', 0 )

        if ssl:
            ssl_certfile = self.Attributes.get('ssl-certfile', None )
            ssl_keyfile = self.Attributes.get('ssl-keyfile', None )
            scheme = 'rediss'

        else:
            ssl_keyfile = ssl_certfile = None
            scheme = 'redis'

        if passwd is not None:
            _passwd = '*' * len(passwd)
            if isinstance( username, str ):
                cred = f"{username}:{_passwd}@"

            else:
                cred = f"{_passwd}@"

        else:
            cred = ''

        url = f"{scheme}://{cred}{host}:{port}/{database}"
        task_result = PluginResult( self )
        if redis is not None:
            try:
                session = redis.Redis( host, port, database, passwd, ssl = ssl, ssl_keyfile = ssl_keyfile, ssl_certfile =ssl_certfile, username = username  )
                task_result.update( True, "" )
                _type = self.Attributes.get( 'type', 'counter' )
                if _type == 'counter' and self.__token is not None:
                    if session.exists( self.__token ):
                        value = int( session.get( self.__token ) )
                        if self.__counter == value:
                            task_result.update( True, f"Redis {url} counter {value} on token {self.__token}" )

                        else:
                            task_result.update( False, f"Redis {url} token {self.__token} counter {value} missed a beat, expected {self.__counter}")

                    else:
                        task_result.update(True, f"Redis {url} initialize counter {self.__counter+1} for token {self.__token}" )

                    self.__counter += 1
                    while session.get( self.__token ) is None or int( session.get( self.__token ) ) != self.__counter:
                        session.set( self.__token, str(self.__counter) )
                        time.sleep(.5)

                session.close()

            except ConnectionError:
                task_result.update(False, f"'redis' {url} Connection ERROR" )

            except TimeoutError:
                task_result.update(False, f"'redis' {url} Connection Timeout ERROR")

            except Exception as exc:
                self.log.exception( f"During REDIS {url}" )
                task_result.update(False, f"'redis {url}' package thrown an exception: {exc}",
                                   {const.C_EXCEPTION: str( exc ),
                                    const.C_TRACEBACK: traceback.format_exc()},
                                   filename=url)

        else:
            task_result.update( False, "Python 'redis' package not installed",
                                   { const.C_EXCEPTION: "ModuleNotFoundError: No module named 'redis'",
                                     const.C_TRACEBACK: traceback.format_stack() },
                                   filename = url )

        API.QUEUE.put( task_result )
        return