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
from mako.template import Template
from datetime import datetime, timedelta, date, time
import pymysql
import pymysql.cursors
from pymysql.err import MySQLError
from sysinvest.common.plugin import PluginResult
import sysinvest.common.api as API
from sysinvest.common.dbutil import SqlMonitorPlugin


class MySqlMonitor( SqlMonitorPlugin ):
    def __init__( self, parent, obj ):
        super().__init__( parent, obj, ( 'mysql','mariadb' ) )
        return

    def execute( self ) -> bool:
        super().execute()
        task_result = PluginResult( self )
        task_result.update( True, "" )
        try:
            self.getDatabaseConfig()
            resultType = self.Attributes.get( 'type', 'rows' )
            with pymysql.connect( host = self.Host, port = self.Port, user = self.Username, password = self.Password, database = self.Database,
                                  cursorclass = pymysql.cursors.Cursor if resultType == 'scalar' else pymysql.cursors.DictCursor ) as connection:
                with connection.cursor() as cursor:
                    # Read a single record
                    parameters: dict = self.Attributes.get('parameters', {})
                    parameters.update( datetime=datetime, timedelta=timedelta,
                                       date=date, time=time)
                    query = Template(self.Attributes.get('query')).render(**parameters)
                    cursor.execute( query )
                    reccount = self.Attributes.get('reccount', None )
                    if isinstance( reccount, int ) and cursor.rowcount != reccount:
                        # Fail
                        task_result.update(False, f'record count mismatch, expected {reccount}, got {cursor.rowcount}')

                    if task_result.Result:
                        self.verifyDatabaseResult( cursor, task_result )

        except ValueError as exc:
            task_result.update( False, f"{exc}" )

        except MySQLError as exc:
            task_result.update( False, f"{exc}" )

        API.QUEUE.put( task_result )
        return task_result.Result