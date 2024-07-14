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
import logging
from sysinvest.common.plugin_base import PluginBase


class ReportPlugin( PluginBase ):
    def __init__( self, name: str, config: dict ):
        super().__init__( config.get( name, {} ) )
        self.__name = name
        self.log = logging.getLogger( f"report.{self.__class__.__name__}")
        self.log.info( f"Config {name}: {self.Config}" )
        return

    @property
    def Name( self ):
        return self.__name

    def notify( self, result: 'PluginResult' ):
        raise NotImplemented()

    def publish( self ):
        raise NotImplemented()



