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
from sysinvest.common.plugin import PluginResult
import sysinvest.common.api as API
from sysinvest.common.dbutil import SqlMonitorPlugin
import cx_Oracle



class OracleMonitor( SqlMonitorPlugin ):
    def __init__( self, parent, obj ):
        super().__init__( parent, obj, ( 'oracle', ) )
        return

    # C_QUERY_EVENT_LIST = """SELECT state as STATE
    #         , Module_id as MODULE_ID
    #         , DT
    #        , count(*) as COUNTER
    # FROM (
    #          select case when state = 1 then 'Waiting'
    #             when state = 2 then 'Active'
    #             when state = 4 then 'Queue'
    #             when state = 5 then 'Depending'
    #             when state = 6 then 'Incorrect'
    #                            else to_char(state)
    #        end as STATE
    #      , module_id
    #       , to_char(e.START_TIME,'YYYY-MM-DD') as dt
    #       FROM {dbSchema}.event e
    #    WHERE state not in (  3 , 7)
    #  )
    # group BY state , module_id , dt
    # ORDER BY 3 desc , 1 , 2"""
    def execute( self ):
        super().execute()
        self.update( True, "" )
        try:
            self.getDatabaseConfig()
            resultType = self.Attributes.get('type', 'rows')
            with cx_Oracle.connect( user = self.Username, password = self.Password, dsn = self.Dsn ) as connection:
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
                        self.update(False, f'record count mismatch, expected {reccount}, got {cursor.rowcount}')

                    if self.Result:
                        self.verifyDatabaseResult( cursor, self )

        except ValueError as exc:
            self.update( False, f"{exc}" )

        except cx_Oracle.DatabaseError as exc:
            self.update( False, f"{exc}" )

        API.QUEUE.put( self )
        return