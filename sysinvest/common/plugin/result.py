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
import json
from datetime import datetime, date, time, timedelta
from mako.template import Template
import mako.exceptions
import sysinvest.common.plugin.constants as const
import logging


class PluginResultEncoder( json.JSONEncoder ):
    def default( self, obj ):
        if isinstance( obj, Exception ):
            return str( obj )

        return obj


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


class PluginResult( object ):
    EXC_TEMPLATE    = "${name} => ${result} ${message}"
    TEMPLATE        = "${name} => ${result}"

    def __init__( self, plugin: 'Plugin' ):
        self.log = logging.getLogger( 'result' )
        self.__result = False
        self.__message = 'Collecting data'
        self.__state = 1
        self.__data = {}
        self.__plugin = plugin
        for k, v in self.__plugin.Monitor.info().items():
            self.__data[ k ] = v

        return

    def update( self, result: bool, message: str, data: dict = None, **kwargs ):
        self.__state = 2
        self.__result = result
        self.__message = message
        self.__data.update( data if isinstance( data, dict ) else {} )
        for k, v in kwargs.items():
            self.__data[ k ] = v

        for k, v in self.Plugin.Monitor.info().items():
            self.__data[ k ] = v

        self.log.info( f"PluginResult.update( {result}, '{message}', {data}, **{kwargs} )" )
        return

    @property
    def Name( self ) -> str:
        return self.__plugin.Name

    @property
    def Result( self ) -> bool:
        return self.__result

    @Result.setter
    def Result( self, value: bool ):
        self.__result = value
        return

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

    @property
    def Plugin( self ) -> 'Plugin':
        return self.__plugin

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

            template = self.Plugin.Template if self.Plugin.Template is not None else self.TEMPLATE
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

    def __repr__(self):
        return f"<PluginResult {self.buildMessage()}>"

    def dump( self ):
        print( f"PluginResult {self.Name}: {self.__result} :: {self.__message}" )
        if self.__data:
            print( self.__data )

    def toJson( self ):
        return {
            "name": self.Name,
            "result": self.Result,
            "message": self.buildMessage()
        }