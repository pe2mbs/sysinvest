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
from typing import Optional
import time
import logging
from datetime import datetime
from sysinvest.common.plugin.base import PluginBase
import sysinvest.common.plugin.constants as const
from datetime import datetime, date, time, timedelta
from mako.template import Template
import mako.exceptions


class HasAttribute( object ):
    def __init__( self, attrs ):
        self.__attrs = attrs
        return

    def __call__(self, *args, **kwargs):
        result = True
        for arg in args:
            if arg not in self.__attrs:
                result = False
                break

        return result


MONITOR_STATE_INIT          = 0
MONITOR_STATE_COLLECTING    = 1
MONITOR_STATE_IDLE          = 3


class MonitorPlugin( PluginBase ):
    EXC_TEMPLATE    = "${name} => ${result} ${message}"
    TEMPLATE        = "${name} => ${result}"

    def __init__( self, parent, config: dict ):
        super().__init__( config, parent )
        self.__lasttime     = 0
        self.__result       = None
        self.__data         = {}
        self.__runOnStartup = False
        self.log            = logging.getLogger( f"plugin.{self.__class__.__name__}")
        self._state         = MONITOR_STATE_INIT
        self.__hit          = 0
        return

    def _getName( self ) -> str:
        return self._config.get( const.C_NAME, 'unknown' )

    def _getEnabled( self ) -> bool:
        return self._config.get( 'enabled', False )

    @property
    def RunOnStartup( self ) -> bool:
        return self.__runOnStartup

    @property
    def Cron( self ) -> str:
        return self._config.get( const.C_CRON, '*/5 * * * *' )

    @property
    def Group( self ) -> str:
        return self._config.get( const.C_GROUP, '*' )

    @property
    def Priority( self ) -> bool:
        return self._config.get( const.C_PRIORITY, False )

    @property
    def Attributes( self ) -> dict:
        return self._config.get( const.C_ATTRIBUTES, {} )

    @property
    def LastTime( self ) -> int:
        return self.__lasttime

    def LastDateTime( self ) -> datetime:
        return datetime.fromtimestamp( self.__lasttime )

    @property
    def Template( self ):
        templateFile = self._config.get( 'template_file' )
        if templateFile:
            self.log.info( f'Loading template file: {templateFile}' )
            with open( templateFile ) as stream:
                return stream.read()

        if hasattr( self, 'DEFAULT_TEMPLATE' ):
            default_templ = self.DEFAULT_TEMPLATE

        else:
            default_templ = "${name} => ${result} ${message}"

        return self._config.get( 'template', default_templ ).replace( '\\n', '\n' )

    def runOnStartup( self ) -> None:
        self.__runOnStartup = True
        return

    def execute( self ) -> None:
        self.__lasttime = time.time()
        self.__hit += 1
        return

    @property
    def Ticket( self ):
        return self.Config.get( 'ticket', True )

    @property
    def Hits( self ) -> int:
        hits = self.Config.get( 'hits', 1 )
        self.log.info( f"Configured hits: {hits}" )
        return hits


    def hitsReached( self ) -> bool:
        hits = self.Config.get('hits', 1)
        self.log.info(f"hitsReached: {hits >= self.__hit} (hit counter: {self.__hit}/{hits})")
        return self.Hits >= self.__hit

    def resetHits( self ):
        self.log.info(f"Reset hit counter: {self.__hit}")
        self.__hit = 0
        return

    @property
    def Result( self ) -> int:
        return self.__result

    @Result.setter
    def Result( self, value ):
        self.__result = value
        return

    @property
    def Status( self ):
        return 'WARNING' if self.__result is None else self.__result.Result

    @property
    def Message( self ):
        return 'Initializing' if self.__result is None else self.__result.Message

    def dump( self ):
        print( f"MonitorPlugin {self.Name}: {self.__result} :: {self.__message}" )
        if self.__data:
            print( self.__data )

    def toJson( self ):
        return {
            "name": self.Name,
            "result": self.Result,
            "message": self.buildMessage()
        }

    def buildMessage( self, translate: Optional[list] = None ) -> str:
        result = ''
        kwargs = {
            'result': self.__result,
            'name': self.Name,
            'message': self.__message,
        }
        kwargs.update( self.__data )
        kwargs[ 'hasAttribute' ] = HasAttribute( kwargs )
        kwargs[ 'datetime' ] = datetime
        kwargs[ 'date' ] = date
        kwargs[ 'time' ] = time
        kwargs[ 'timedelta' ] = timedelta
        try:
            if const.C_EXCEPTION in self.__data:
                return Template( self.EXC_TEMPLATE ).render( **kwargs )

            template = self.Template if self.Template is not None else self.TEMPLATE
            result = Template( template ).render( **kwargs ).strip( ' \r\n' )
            if isinstance( translate, list ):
                try:
                    for ch, tr in translate:
                        result = result.replace( ch, tr )

                except Exception:
                    self.log.exception( f"During translate " )

        except NameError:
            self.log.error( f"{mako.exceptions.text_error_template().render()}\n{kwargs}" )

        return result

    def update( self, result: bool, message: str, data: dict = None, **kwargs ):
        self.__state = 2
        self.__result = result
        self.__message = message
        self.__data.update( data if isinstance( data, dict ) else {} )
        for k, v in kwargs.items():
            self.__data[ k ] = v

        for k, v in self.Parent.info().items():
            self.__data[ k ] = v

        self.log.info( f"MonitorPlugin.update( {result}, '{message}', {data}, **{kwargs} )" )
        return