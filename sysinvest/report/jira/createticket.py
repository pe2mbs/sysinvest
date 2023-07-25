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
from sysinvest.common.plugin import PluginResult, MonitorPlugin, ReportPlugin
from sysinvest.common.proxy import ProxyMixin
try:
    from jira import JIRA
    from requests.exceptions import ConnectionError

except:
    JIRA = None


class ReportJira( ReportPlugin, ProxyMixin ):
    def __init__( self, config: dict ):
        super().__init__( 'jira', config )
        ProxyMixin.__init__( self, self.Config.get( 'proxy', None ) )
        return

    def notify( self, result: PluginResult ):
        # All is handled here
        plugin: MonitorPlugin = result.Plugin
        if plugin.Ticket and not result.Result:
            if not plugin.hitsReached():
                # Dont send a ticket just yet, wait for the next notify() call
                return

            server = self.Config.get( 'host', {} )
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
                jira = JIRA( server,
                             basic_auth = ( ( self.Config.get( 'username' ), self.Config.get('password' ) ) ),
                             options = { "server": server,
                                         "verify": self.sslVerify,
                                         "check_update": True,
                                         },
                             validate = True,
                             logging = True,
                             proxies = self.resolveViaProxy( server ) )

                query = f'summary ~ "{plugin.Name}" and status != Closed'
                jiraIssues = jira.search_issues( query )
                if isinstance( jiraIssues, dict ) and len( jiraIssues ) > 0:
                    self.log.warning( f"Jira Issue found: {jiraIssues} with status {jiraIssues}" )

                elif isinstance( jiraIssues, list ) and len( jiraIssues ) > 0:
                    for issue in jiraIssues:
                        status  = issue.raw.get('fields',{}).get('status',{}).get('name', 'UNKNOWN' )
                        self.log.warning( f"Jira Issue(s) found: {issue.key} with status '{status}'" )

                else:
                    new_issue = jira.create_issue( project = project,
                                                   summary = plugin.Name,
                                                   description = result.buildMessage(),
                                                   priority = { "name": 'Critical' },
                                                   issuetype = { 'name': self.Config.get( 'issue', 'Bug' ) } )
                    for watcher in self.Config.get( 'watchers', [] ):
                        jira.add_watcher( new_issue, watcher )

                    self.log.warning(f"Jira Issue created: {new_issue}")

                plugin.resetHits()

            except ConnectionError:
                self.log.error( f"Could not connect to {server}" )

            except Exception as exc:
                self.log.exception( "During JIRA update" )


        return

    def publish( self ):
        # Does notthing
        return
