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
from common.plugin import PluginResult, MonitorPlugin
from mako.template import Template
from mako import exceptions
from datetime import datetime
from threading import RLock
from common.plugin import ReportPlugin
import os


class WriteHtmlPage( ReportPlugin ):
    def __init__( self, config: dict ):
        super().__init__( 'html', config )
        self.log = logging.getLogger( 'html' )
        self.log.info( f"Initialize reporter html: {self.Config}" )
        self.__render = {}
        self.__lock = RLock()
        return

    def notify( self, result: PluginResult ):
        self.log.info( f"{result.Name} notify" )
        self.__lock.acquire()
        self.__render[ result.Name ] = result
        self.log.info( self.__render )
        self.publish()
        self.__lock.release()
        return

    def publish( self ):
        template_filename = self.Config.get( 'template', 'template_index.html' )
        if not template_filename.startswith( '/' ) and ':' not in template_filename:
            template_filename = os.path.join( os.curdir, template_filename )

        with open( template_filename, 'r' ) as stream:
            template = Template( stream.read() )

        interval = self.Config.get( 'interval', 5 )
        try:
            template_rendered = template.render( pluginResults = self.__render,
                                                 interval = interval,
                                                 lastTime = datetime.now().strftime( "%Y-%m-%d - %H:%M:%S") )
        except:
            print( exceptions.text_error_template().render() )
            raise

        output_filename = self.Config.get( 'location', 'index.html' )
        if not output_filename.startswith( '/' ) and ':' not in output_filename:
            output_filename = os.path.join( os.curdir, output_filename )

        with open( output_filename, 'w' ) as stream:
            stream.write( template_rendered )

        return
