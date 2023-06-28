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
try:
    from jira import JIRA

except:
    JIRA = None


class ReportJira( ReportPlugin ):
    def __init__( self, config: dict ):
        super().__init__( 'jira', config )
        return

    def notify( self, result: PluginResult ):
        # All is handled here

        return

    def publish( self ):
        # Does notthing
        return

    def sendmail( self, group: str, message: str, subject: Optional[str] = None, attachments: Optional[list] = None ):
        # host:           jira.pe2mbs.nl
        jiraProject = self.__cfg.get( 'project', {} )
        host = jiraProject.get( 'project', {} )
        if not isinstance( host, str ):
            raise Exception( f"jira.host parameter not configured" )

        project = jiraProject.get( 'project' )
        if not isinstance( project, str ):
            raise Exception( f"jira.project parameter not configured" )

        jira = JIRA( host, auth = ( jiraProject.get( 'username' ), jiraProject.get( 'password' ) ) )
        new_issue = jira.create_issue( project = project,
                                       summary = subject,
                                       description = message,
                                       issuetype = {'name': jiraProject.get( 'issue', 'Bug' ) } )
        assignee = jiraProject.get( 'assignee' )
        if isinstance( assignee, str ):
            new_issue.update( assignee = { 'name': assignee } )

        admin = jiraProject.get( 'groups', {} ).get( 'admin', [] )
        addressees = jiraProject.get( 'groups', {} ).get( group, [] )
        if len( addressees ) == 0:
            addressees = admin

        for username in addressees:
            jira.add_watcher( new_issue, username )

        # read and upload a file (note binary mode for opening, it's important):
        if isinstance( attachments, list ):
            for filename in attachments:
                with open( filename, 'rb') as f:
                    jira.add_attachment( issue = new_issue, attachment = f )

        return
