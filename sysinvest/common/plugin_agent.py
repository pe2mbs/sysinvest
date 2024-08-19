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
import typing as t
import logging
from datetime import datetime, timezone
from sysinvest.common.interfaces import TaskStatus, ExceptionData
from   sysinvest.common.plugin_base import PluginBase
import sysinvest.common.constants as const


class MonitorPluginAgent( PluginBase ):
    def __init__( self, parent, config: dict ):
        super().__init__( config, parent )
        self.log            = logging.getLogger( f"plugin.{self.__class__.__name__}")
        self.__runOnStartup = True
        self.__hits         = 0
        self.__since        = datetime.utcnow().replace( tzinfo = timezone.utc )
        return

    @property
    def Since( self ):
        return self.__since

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

    def runOnStartup( self ) -> None:
        self.__runOnStartup = True
        return

    def execute( self ) -> TaskStatus:
        result = super().execute()
        self.incrementHit()
        return result

    @property
    def Ticket( self ):
        return self.Config.get( 'ticket', True )

    @property
    def LastTime( self ) -> t.Union[ int, datetime ]:
        return self.serverData.lasttime

    def LastDateTime( self ) -> datetime:
        return datetime.fromtimestamp( self.__serverData.lasttime )

    @property
    def MaxHits( self ) -> int:
        maxhits = self.Config.get( 'hits', 1 )
        self.log.info( f"Configured hits: { maxhits }" )
        return maxhits

    def hitsReached( self ) -> bool:
        maxhits = self.Config.get( 'hits', 1 )
        self.log.info( f"hitsReached: {maxhits <= self.__hits} (hit counter: {self.__hits}/{maxhits})")
        return maxhits <= self.__hits

    def incrementHit( self ):
        self.__hits += 1
        self.log.info( f"Increment hit counter: { self.__hits }" )
        return

    def resetHits( self ):
        self.log.info(f"Reset hit counter: {self.__hits}")
        self.__hits = 0
        return

    def setExceptionData( self, exc, stack ):
        self.setServerData( ExceptionData( exception = str( exc ),
                                           stacktrace = list( [ f"File {line.filename}, line {line.lineno}, in {line.line}" for line in stack ] ) ) )
        return

