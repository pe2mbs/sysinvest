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
import os.path
import traceback
import time
import urllib.parse
from sysinvest.common.interfaces import TaskStatus, ExceptionData
from sysinvest.common.plugin_agent import MonitorPluginAgent
try:
    import redis
    import redis.exceptions

except ModuleNotFoundError:
    redis = None


class RedisAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj ):
        super().__init__( parent, obj )
        self.__counter = 0
        return

    def execute( self ) -> TaskStatus:
        super().execute()
        url         = self.Config.get( 'url', None )
        cert        = self.Config.get( 'cert', None )
        key         = self.Config.get( 'key', None )
        self.Status = TaskStatus.FAILED
        try:
            if redis is None:
                raise ModuleNotFoundError( 'redis' )

            scheme = 'redis'
            if isinstance( cert, str ):
                scheme = 'rediss'
                if not os.path.exists( cert ):
                    raise FileNotFoundError( cert )

                if isinstance( key, str ) and not os.path.exists( key ):
                    raise FileNotFoundError( key )

            self.log.info( f"REDIS checking: {url}")
            url_info = urllib.parse.urlparse( url )
            if url_info.scheme != scheme:
                raise Exception( "Invalid scheme" )

            database = int( str( url_info.path ).strip('/') )
            session = redis.Redis( url_info.hostname, url_info.port, database, url_info.password,
                                   ssl = True if isinstance( cert, str ) else False,
                                   ssl_keyfile = key,
                                   ssl_certfile =cert,
                                   username = url_info.username if url_info.username not in ( None, '', 'null' ) else None )
            self.Status = TaskStatus.OK
            token = self.Config.get( 'token', 'sysinvest.agent.plugins.redis' )
            _type = self.Config.get( 'type', 'counter' )
            if _type == 'counter' and token is not None:
                if session.exists( token ):
                    value = session.get( token )
                    if isinstance( value, bytes ):
                        value = int( value )
                        if self.__counter == value:
                            self.Message = f"{ url } counter { value } on token { token }"

                        else:
                            self.Status = TaskStatus.FAILED
                            self.Message = f"{ url } token { token } counter { value } missed a beat, expected { self.__counter }"

                else:
                    self.Message = f"{ url } initialize counter { self.__counter + 1 } for token { token }"
                    self.Status = TaskStatus.COLLECTING

                self.__counter += 1
                while not isinstance( session.get( token ), bytes ) or int( session.get( token ) ) != self.__counter:
                    session.set( token, str(self.__counter) )
                    time.sleep( .5 )

            session.close()

        except (ConnectionError, redis.exceptions.ConnectionError):
            self.Message = f"{url} Connection ERROR"
            self.Status = TaskStatus.FAILED

        except TimeoutError:
            self.Message = f"{url} Connection Timeout ERROR"
            self.Status = TaskStatus.FAILED

        except ModuleNotFoundError:
            self.Message = "Python 'redis' package not installed"

        except Exception as exc:
            self.Status = TaskStatus.FAILED
            self.log.exception( f"During REDIS {url}" )
            self.setExceptionData( exc, traceback.extract_stack() )

        return self.Status
