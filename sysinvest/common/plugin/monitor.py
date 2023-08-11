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


class MonitorPlugin( PluginBase ):
    EXC_TEMPLATE    = "${name} => ${result} ${message}"
    TEMPLATE        = "${name} => ${result}"

    def __init__( self, parent, config: dict ):
        super().__init__( config, parent )
        self.__lasttime = 0
        self.__runOnStartup = False
        self.__hit = 0
        self.log = logging.getLogger( f"plugin.{self.__class__.__name__}")
        self.__status = const.C_STATUS_INIT
        self.__message = 'Collecting data'
        self.__data = {}
        return

    @property
    def RunOnStartup( self ) -> bool:
        return self.__runOnStartup

    @property
    def Enabled( self ) -> bool:
        return self.Config.get( const.C_ENABLED, False )

    @property
    def Cron( self ) -> str:
        return self.Config.get( const.C_CRON, '*/5 * * * *' )

    @property
    def Group( self ) -> str:
        return self.Config.get( const.C_GROUP, '*' )

    @property
    def Priority( self ) -> bool:
        return self.Config.get( const.C_PRIORITY, False )

    @property
    def Name( self ) -> str:
        return self.Config.get( const.C_NAME, 'unknown' )

    @property
    def Attributes( self ) -> dict:
        return self.Config.get( const.C_ATTRIBUTES, {} )

    @property
    def LastTime( self ) -> int:
        return self.__lasttime

    def LastDateTime( self ) -> datetime:
        return datetime.fromtimestamp( self.__lasttime )

    def update( self, status: int, message: str, data: dict = None, **kwargs ):
        self.__status = status
        self.__message = message
        self.__data.update( data if isinstance( data, dict ) else {} )
        for k, v in kwargs.items():
            self.__data[ k ] = v

        self.log.info( f"MonitorPlugin.update( {status}, '{message}', {data}, **{kwargs} )" )
        return

    @property
    def Status( self ) -> int:
        return self.__status

    @Status.setter
    def Status( self, value: int ):
        self.__status = value
        return

    @property
    def StatusString( self ):
        STRINGS = {
            const.C_STATUS_INIT:      "Initializing",
            const.C_STATUS_OKE:       "Oke",
            const.C_STATUS_WARNING:   "Warning",
            const.C_STATUS_ERROR:     "Failed",
        }
        return STRINGS[ self.__status ]

    @property
    def Message( self ) -> str:
        return self.__message

    @Message.setter
    def Message( self, value: str ):
        self.__message = value
        return

    @property
    def Details( self ) -> dict:
        return self.__data

    def buildMessage( self, translate: Optional[list] = None ) -> str:
        result = ''
        kwargs = {
            const.C_STATUS: self.__status,
            const.C_NAME: self.Name,
            const.C_MESSAGE: self.__message,
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
            try:
                result = Template( template ).render( **kwargs ).strip( ' \r\n' )

            except Exception:
                self.log.error( mako.exceptions.text_error_template() )

            if isinstance( translate, list ):
                try:
                    for ch, tr in translate:
                        result = result.replace( ch, tr )

                except Exception:
                    self.log.exception( f"During translate " )


        except NameError:
            self.log.error( f"{mako.exceptions.text_error_template().render()}\n{kwargs}" )

        return result

    def __repr__(self):
        return f"<MonitorPlugin {self.buildMessage()}>"

    def dump( self ):
        print( f"MonitorPlugin {self.Name}: {self.__status} :: {self.__message}" )
        if self.__data:
            print( self.__data )

    def toJson( self ):
        return {
            const.C_STATUS: self.__status,
            const.C_NAME: self.Name,
            const.C_MESSAGE: self.buildMessage(),
        }

    @property
    def Template( self ):
        templateFile = self.Config.get( 'template_file' )
        if templateFile:
            self.log.info( f'Loading template file: {templateFile}' )
            with open( templateFile ) as stream:
                return stream.read()

        if hasattr( self, 'DEFAULT_TEMPLATE' ):
            default_templ = self.DEFAULT_TEMPLATE

        else:
            default_templ = "${name} => ${result} ${message}"

        return self.Config.get( 'template', default_templ ).replace( '\\n', '\n' )

    def runOnStartup( self ) -> None:
        self.__runOnStartup = True
        return

    def execute( self ) -> None:
        self.__lasttime = time.time()
        self.__hit += 1
        return

    @property
    def Ticket( self ):
        return self.Config.get( const.C_TICKET, True )

    @property
    def Hits( self ) -> int:
        hits = self.Config.get( const.C_HITS, 1 )
        self.log.info( f"Configured hits: {hits}" )
        return hits

    def hitsReached( self ) -> bool:
        hits = self.Config.get( const.C_HITS, 1 )
        self.log.info( f"hitsReached: {hits >= self.__hit} (hit counter: {self.__hit}/{hits})" )
        return self.Hits >= self.__hit

    def resetHits( self ):
        self.log.info( f"Reset hit counter: {self.__hit}" )
        self.__hit = 0
        return
