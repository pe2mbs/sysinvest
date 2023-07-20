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
import time
import logging
from datetime import datetime
from sysinvest.common.plugin.base import PluginBase
import sysinvest.common.plugin.constants as const


class MonitorPlugin( PluginBase ):
    def __init__( self, parent, config: dict ):
        super().__init__( config, parent )
        self.__lasttime = 0
        self.__runOnStartup = False
        self.log = logging.getLogger( f"plugin.{self.__class__.__name__}")
        return

    @property
    def RunOnStartup( self ) -> bool:
        return self.__runOnStartup

    @property
    def Enabled( self ) -> bool:
        return self.Config.get( 'enabled', False )

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
        return
