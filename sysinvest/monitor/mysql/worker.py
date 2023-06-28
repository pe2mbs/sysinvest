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
from itertools import zip_longest
from mako.template import Template
from datetime import datetime, timedelta, date, time
from sysinvest.common.plugin import MonitorPlugin, PluginResult
import mysql.connector
from mysql.connector import errorcode

class MySql( MonitorPlugin ):
    def execute( self ):
        super().execute()
        task_result = PluginResult( self )
        cnx = None
        cursor = None
        try:
            cnx = mysql.connector.connect( user=self.Attributes.get('username'),
                                       password=self.Attributes.get('password'),
                                       host=self.Attributes.get('host'),
                                       database=self.Attributes.get('database'))
            cursor = cnx.cursor()
            parameters: dict = self.Attributes.get( 'parameters', {} )
            parameters.update( datetime = datetime,
                               timedelta = timedelta,
                               date = date,
                               time = time )
            query = Template( self.Attributes.get( 'query' ) ).render( **parameters )
            cursor.execute( query )
            records = cursor.fetchall()
            reccount = self.Attributes.get( 'reccount' )
            if isinstance( reccount, int ):
                if len( records ) != reccount:
                    task_result.update( False, f'record count mismatch, expected {reccount}, got {len( records )}' )

                else:
                    task_result.update( True, "Record count matches" )

            elif self.Attributes.get( 'results' ):
                results = self.Attributes.get( 'results' )
                if isinstance( results, list ):
                    pass

                elif isinstance( results, dict ):
                    if len( results ) != reccount:
                        task_result.update( False, f'record count mismatch, expected {reccount}, got {len( results )}' )
                        raise ValueError

                    else:
                        # Make it back into a list
                        results = [ results ]

                else:
                    # To jump out
                    raise PluginResult( self, False, f"Invalid 'results' in plugin config '{self.Name}'" )

                for row, (dbRecord, cfgRecord) in enumerate( zip_longest( records, results ) ):
                    # Now compare the records, we assume a 1:1 compare
                    for col, (dbField, cfgField) in enumerate( zip( dbRecord, cfgRecord ) ):
                        if dbField != cfgField:
                            task_result.update( False, f"Record {row} don't match in column {col} plugin '{self.Name}'",
                                                   dbRecord = dbRecord, cfgRecord = cfgRecord, dbField = dbField, cfgField = cfgField )
                            break

            else:
                task_result.update( False, f"'results' nor 'reccount' configured in plugin config '{self.Name}'" )

        except ValueError:
            pass

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                task_result.update( False, "Something is wrong with your user name or password" )

            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                task_result.update( False, "Database does not exist" )

            else:
                task_result.update( False, "Other error" )

        finally:
            if cursor is not None:
                cursor.close()

            if cnx is not None:                     # noqa
                cnx.close()             # noqa

        self.Monitor.Queue.put( task_result )
        return