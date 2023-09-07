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
from sysinvest.common.plugin import PluginResult, MonitorPlugin
from threading import Thread
from mako.template import Template
from mako import exceptions
import sysinvest.version as version
from flask import Flask
from datetime import datetime
from threading import RLock
from sysinvest.common.plugin import ReportPlugin
import os
from datetime import datetime
import time
import socket

app = Flask( __name__ )
page = None


def startWebServer():
    port = 5050
    host = 'localhost'
    if not isinstance( page, WriteHtmlPage ):
        return

    server = page.Config.get('server', {} )
    host = server.get( 'host', host )
    port = server.get( 'port', port )
    app.run( host = host, port = port )
    return


@app.route("/")
def index():
    global page
    if isinstance( page, WriteHtmlPage ):
        return page.buildPage( page.Config.get( 'interval', 5 ) )

    return "<p>Monitor Currently not available!</p>"


@app.route("/sysinvest/")
def sysinvest():
    global page
    if isinstance( page, WriteHtmlPage ):
        return page.buildPage( page.Config.get( 'interval', 5 ) )

    return "<p>Monitor Currently not available!</p>"



class WriteHtmlPage( ReportPlugin ):
    def __init__( self, config: dict ):
        super().__init__( 'html', config )
        # self.log = logging.getLogger( 'html' )
        self.log.info( f"Initialize reporter html: {self.Config}" )
        self.__issuesDetected = {}
        self.__render = {}
        self.__lock = RLock()
        self.__template = None
        self.loadTemplate()
        # Assign current instance to global variable, for the web server
        global page
        page = self
        server = self.Config.get('server', {})
        active = server.get('enabled', False)
        if active:
            self.log.warning( f"Starting web server: {server}")
            self.__pageThread = Thread( target = startWebServer )
            self.__pageThread.start()
        else:
            self.log.warning( "Not starting web server" )

        return

    def loadTemplate( self ):
        template_filename = self.Config.get( 'template', 'template_index.mako' )
        if not template_filename.startswith( '/' ) and ':' not in template_filename:
            # relative path
            module_direcory = os.path.abspath( os.path.dirname( __file__ ) )
            package_direcory = os.path.abspath( os.path.join( module_direcory, '..', '..' ) )

            for directory in ( os.curdir, module_direcory, package_direcory ):
                tmp = os.path.join( directory, template_filename )
                self.log.debug( f"Searching: {tmp}" )
                if os.path.exists( tmp ):
                    template_filename = tmp
                    break

            if not os.path.exists( template_filename ):
                raise FileNotFoundError( f"Could not find template {template_filename}" )

        if not os.path.exists( template_filename ):
            raise FileNotFoundError( f"Could not find template {template_filename}" )

        self.log.info( f"Loading template {template_filename}")
        with open( template_filename, 'r' ) as stream:
            self.__template = Template( stream.read() )

        return

    def notify( self, result: PluginResult ):
        self.__lock.acquire()
        self.__render[ result.Name ] = result
        tm = datetime.now().strftime( "%Y-%m-%d %h:%m" )
        for key, value in self.__render.items():
            self.log.info( f"notify item: {key} = {value}" )
            if not value.Result:
                self.__issuesDetected.setdefault( tm, 0 )
                self.__issuesDetected[ tm ] += 1

        self.publish()
        self.__lock.release()
        return

    def publish( self ):
        self.log.info( f"Publish {len(self.__render)}")
        if self.__template is None:
            raise Exception( "template not loaded" )

        remove = []
        for name, obj in self.__render.items():
            obj: PluginResult
            if not obj.Plugin.Enabled:
                remove.append( name )

        for name in remove:
            del self.__render[ name ]

        template_rendered = self.buildPage( self.Config.get( 'interval', 5 ) )

        self.log.info( f"Writing page {len(template_rendered)} bytes")
        output_filename = self.Config.get( 'location', 'index.html' )

        if not output_filename.startswith('/') and ':' not in output_filename:
            output_filename = os.path.join(os.curdir, output_filename)

        filepath, filename = os.path.split( output_filename )
        _filename = os.path.join( filepath, f"_{filename}" )
        try:
            with open( _filename, 'w' ) as stream:
                stream.write( template_rendered )

        except:
            self.log.exception("During writing of the temp. file")

        cnt = 5
        while cnt > 0 and os.path.exists( _filename ):
            cnt -= 1
            try:
                if os.path.exists( output_filename ):
                    os.remove( output_filename )

                os.rename( _filename, output_filename )
            except:
                if cnt == 0:
                    raise

                self.log.error( "Try To rename file, failed" )
                time.sleep(1)

        return

    def buildPage( self, interval ):
        self.log.info( f"Render page {len(self.__render)}")
        try:
            template_rendered = self.__template.render( pluginResults = self.__render,
                                                        interval = interval,
                                                        config = self.Config,
                                                        reporter = self,
                                                        issuesDetected = self.__issuesDetected,
                                                        release = version,
                                                        lastTime = datetime.now().strftime( "%Y-%m-%d - %H:%M:%S"),
                                                        computername = socket.gethostbyaddr(socket.gethostname())[0] )
        except:
            self.log.error( exceptions.text_error_template().render() )
            raise

        return template_rendered