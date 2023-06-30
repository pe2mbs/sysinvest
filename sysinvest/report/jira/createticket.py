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
from typing import Union, Optional
from sysinvest.common.plugin import PluginResult, MonitorPlugin, ReportPlugin
from sysinvest.common.proxy import ProxyMixin
try:
    from jira import JIRA
    from requests.exceptions import ConnectionError

except:
    JIRA = None

# try:
#     import jwt
#
# except:
#     jwt = None

import jwt

class ReportJira( ReportPlugin, ProxyMixin ):
    def __init__( self, config: dict ):
        super().__init__( 'jira', config )
        ProxyMixin.__init__( self, self.Config.get( 'proxy', None ) )
        return

    def notify( self, result: PluginResult ):
        # All is handled here
        if not result.Result:
            server = self.Config.get('host', {})
            if not isinstance( server, str ):
                raise Exception( f"jira.host parameter not configured" )

            project = self.Config.get( 'project' )
            if not isinstance( project, str ):
                raise Exception( f"jira.project parameter not configured" )

            if not isinstance( self.Config.get( 'username' ), str ):
                raise Exception( f"jira.username parameter not configured" )

            if not isinstance( self.Config.get('password' ) , str ):
                raise Exception( f"jira.password parameter not configured" )

            try:
                self.sslVerify = self.Config.get( 'sslverify', True )
                # test-tool-support-sysinvest
                #
                # API Token signature
                # 8N9MD6_tUSpL6Fg_xWQbfn_kKXIj_EbYCzFzeRaobybL2r2wnP1ecud63s2hZcZRB7PUreTjk5Y3ONoLbA4jug
                #
                # API Token
                # eyJhbGciOiJFUzI1NiIsImtpZCI6IktaTi1QUkQtMDAxIn0.eyJpc3MiOiJLYXphbiBVc2VyIE1hbmFnZW1lbnQiLCJhdWQiOiJLYXphbiBVc2VyIE1hbmFnZW1lbnQiLCJzdWIiOiJ0ZXN0LXRvb2wtc3VwcG9ydC1zeXNpbnZlc3QiLCJpc0FkbWluIjpmYWxzZSwidXNlcnR5cGUiOiJLUFJPSkVDVCIsIm5iZiI6MTY4ODA2ODUzMywianRpIjoiMFJSNlFmU1ZGUTNEWHZzbmwyOXRndyIsImlhdCI6MTY4ODA2ODU5M30.8N9MD6_tUSpL6Fg_xWQbfn_kKXIj_EbYCzFzeRaobybL2r2wnP1ecud63s2hZcZRB7PUreTjk5Y3ONoLbA4jug
                token   = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IktaTi1QUkQtMDAxIn0.eyJpc3MiOiJLYXphbiBVc2VyIE1hbmFnZW1lbnQiLCJhdWQiOiJLYXphbiBVc2VyIE1hbmFnZW1lbnQiLCJzdWIiOiJ0ZXN0LXRvb2wtc3VwcG9ydC1zeXNpbnZlc3QiLCJpc0FkbWluIjpmYWxzZSwidXNlcnR5cGUiOiJLUFJPSkVDVCIsIm5iZiI6MTY4ODA2ODUzMywianRpIjoiMFJSNlFmU1ZGUTNEWHZzbmwyOXRndyIsImlhdCI6MTY4ODA2ODU5M30.8N9MD6_tUSpL6Fg_xWQbfn_kKXIj_EbYCzFzeRaobybL2r2wnP1ecud63s2hZcZRB7PUreTjk5Y3ONoLbA4jug'
                headers = { 'Authorization': 'JWT {}'.format( token ) }
                jira = JIRA( server,
                             basic_auth = ( ( self.Config.get( 'username' ), self.Config.get('password' ) ) ),
                             # token_auth = token,
                             options = { "server": server,
                                         "verify": self.sslVerify,
                                         "check_update": True,
                                         # "headers": headers
                                         },
                             validate = True,
                             logging = True,
                             proxies = self.resolveViaProxy( server ) )

                new_issue = jira.create_issue( project = project,
                                               summary = result.Plugin.Name,
                                               description = result.buildMessage(),
                                               issuetype = { 'name': self.Config.get( 'issue', 'Bug' ) } )

            except ConnectionError:
                self.log.error( f"Could not connect to {host}" )

            except Exception as exc:
                self.log.exception( "During JIRA update" )


        return

    def publish( self ):
        # Does notthing
        return
