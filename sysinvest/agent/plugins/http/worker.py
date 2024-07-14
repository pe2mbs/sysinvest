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
from lxml import etree
from sysinvest.common.interfaces import ExceptionData, TaskStatus, HttpResponse, HtmlElement
from sysinvest.common.plugin_agent import MonitorPluginAgent

try:
    import requests

except:
    requests = None


class HttpsAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj  ):
        super().__init__( parent, obj )
        return

    def execute( self ) -> TaskStatus:
        super().execute()
        self.Status = TaskStatus.FAILED
        if requests is not None:
            try:
                kwargs = { }
                self.log.info( f"checking URL {self.Config.get( 'url', 'GET' )}" )
                for attr in ('param', 'headers', 'json', 'timeout', 'verify'):
                    if attr in self.Config:
                        kwargs[ self ] = self.Config[ attr ]

                if 'username' in self.Config:
                    kwargs[ 'auth' ] = (self.Config[ 'username' ], self.Config[ 'password' ])

                if 'cert' in self.Config:
                    if not os.path.exists( self.Config[ 'cert' ] ):
                        raise FileNotFoundError( self.Config[ 'cert' ] )

                    if 'key' in self.Config:
                        if not os.path.exists( self.Config[ 'key' ] ):
                            raise FileNotFoundError( self.Config[ 'key' ] )

                        kwargs[ 'auth' ] = (self.Config[ 'cert' ], self.Config[ 'key' ])

                    else:
                        kwargs[ 'auth' ] = self.Config[ 'cert' ]

                send_content = self.Config.get( 'content', False )
                r = requests.request( self.Config.get( 'method', 'GET' ).upper(), self.Config.get( 'url', 'http://localhost' ), **kwargs )
                response = self.Config.get( 'response', {} )
                self.setServerData( HttpResponse( status_code = r.status_code,
                                                  content =  r.content if send_content else '<Not provided>',
                                                  encoding = r.encoding,
                                                  elapsed = r.elapsed.seconds,
                                                  headers = r.headers ) )
                if r.status_code == self.Config.get( 'status_code', 200 ):
                    self.Status = TaskStatus.OK
                    msg = [ "Result code did match" ]
                    content = response.get( 'content' )
                    self.log.debug( r.content )
                    expected_headers = response.get( 'headers', {} )
                    for key, value in expected_headers.items():
                        if key in r.headers:
                            if r.headers[ key ] != value:
                                msg.append( f"Header '{ key }' dit not match '{ r.headers[ key ] }', expected '{ value }'" )
                                self.Status = TaskStatus.FAILED

                    if len( expected_headers ) and self.Status == TaskStatus.OK:
                        msg.append( f"Headers match" )

                    if isinstance( content, str ):
                        if r.content != content:
                            msg.append( "Content failed" )
                            self.Status = TaskStatus.FAILED

                        else:
                            msg.append( "content match" )

                    elif 'inspect' in self.Config:
                        tree = etree.HTML( r.content )
                        # print( etree.tostring( tree ).decode( 'utf-8' ) )
                        inspections = []
                        for item in self.Config.get( 'inspect', [] ):
                            label = item.get( 'label' )
                            xpath = item.get( 'xpath' )
                            if xpath is None:
                                msg.append( "Missing xpath attribute" )
                                continue

                            if label is None:
                                label = xpath

                            result = tree.xpath( xpath )
                            if isinstance( result, list ):
                                if len( result ) == 1:
                                    result = result[ 0 ]

                            expected = item.get( 'expected' )
                            if isinstance( result, list ):
                                if isinstance( expected, list ):
                                    pass

                                for ires in result:
                                    print( ires.text )

                            else:
                                element = HtmlElement( label = label, value = result.text, valid = expected is None or result.text == expected )
                                if not element.valid:
                                    msg.append( f"{element.label} doesn't match, found {element.value}, expected {expected}")

                                inspections.append( element )

                        if len( inspections ) > 0:
                            self.serverData.elements = inspections

                    self.Message = '\n'.join( msg )

                else:
                    self.Message = f"Result code did match: {r.status_code} expected: { self.Config.get( 'status_code', 200 ) }"

            except Exception as exc:
                self.log.exception( "During lookup process" )
                self.setExceptionData( exc, traceback.extract_stack() )

        else:
            self.log.exception( "During lookup process" )
            self.setExceptionData( 'ModuleNotFound requests', traceback.extract_stack() )

        return self.Status
