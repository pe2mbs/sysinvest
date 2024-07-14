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
import typing as t
import urllib.parse
import importlib
import traceback
import numpy
from itertools import zip_longest
from mako.template import Template
from datetime import datetime, timedelta, date, time
from sysinvest.common.interfaces import TaskStatus, SqlResult
from sysinvest.common.plugin_agent import MonitorPluginAgent


def compare_dict(a, b):
    # Compared two dictionaries..
    # Posts things that are not equal..
    res_compare = []
    for k in set(list(a.keys()) + list(b.keys())):
        if isinstance(a[k], dict):
            z0 = compare_dict( a[ k ], b[ k ] )

        else:
            z0 = a[ k ] == b[ k ]

        z0_bool = numpy.all( z0 )
        res_compare.append(z0_bool)
        if not z0_bool:
            print(k, a[k], b[k])

    return bool( numpy.all(res_compare ) )


class SqlAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj ):
        super().__init__( parent, obj )
        url = urllib.parse.urlparse( obj.get( 'url' ) )
        if url.scheme == 'oracle':
            mod = importlib.import_module('sysinvest.agent.plugins.sql.oracle')

        elif url.scheme in ( 'mariadb', 'mysql' ):
            mod = importlib.import_module('sysinvest.agent.plugins.sql.mysql')

        elif url.scheme in ( 'sqlite', 'sqlite3' ):
            mod = importlib.import_module( 'sysinvest.agent.plugins.sql.sqlite' )

        else:
            raise NotImplemented( f'{url.scheme} not yet supported' )

        self.__sql = getattr( mod, 'SqlClass' )( obj )
        self.__sqlError = getattr( mod, 'SqlError' )
        return

    """
        Currently tested with MYSQL and SQLite3 
    """
    def execute( self ) -> TaskStatus:
        super().execute()
        self.Status = TaskStatus.FAILED
        try:
            msg = []
            with self.__sql.connect() as connection:
                errors = 0
                with connection.cursor() as cursor:
                    # Build and execute the query
                    parameters: dict = self.Config.get( 'parameters', {} )
                    parameters.update( datetime=datetime, timedelta=timedelta, date=date, time=time )
                    query = Template( self.Config.get( 'query' ) ).render( **parameters )
                    cursor.execute( query )
                    resultType = self.Config.get( 'type', 'rows' )
                    info = SqlResult( recordcount = cursor.rowcount, query = query, expected = self.Config.get( 'expected', None ) )
                    self.setServerData( info )
                    if resultType == 'count':
                        if not isinstance( info.expected, int ):
                            raise ValueError( "expected not defined or invalid type" )

                        result = cursor.fetchone()
                        if isinstance( result, tuple ):
                            # SQLite3 returns counts as a tuple with a recount of -1
                            info.recordcount = len( result )
                            info.retrieved = result[ 0 ]

                        elif isinstance( result, dict ):
                            # pymysql returns counts as a dictionary with a recount of 1
                            info.retrieved = list( result.values() )[0]

                        else:
                            raise ValueError( 'Invalid return type' )

                        if info.recordcount != 1:
                            raise ValueError( "Returned value not 1 result" )

                        self.log.info( f"Query result : {result}" )
                        if info.retrieved != info.expected:
                            msg.append( f'Record count mismatch, expected {info.expected}, got {info.retrieved}' )

                        else:
                            self.Status = TaskStatus.OK
                            msg.append( 'Query result OK' )

                    elif resultType == 'scalar':
                        result = cursor.fetchone()
                        if isinstance( result, dict ):
                            if len( result ) != 1:
                                raise ValueError( f"Not a scalar result: {result}" )

                            info.retrieved = list( result.values() )[ 0 ]

                        elif not isinstance( result, tuple ):
                            raise ValueError( f"Not a scalar result: {result}" )

                        else:
                            info.retrieved = result[ 0 ]

                        self.log.info( f"Query result : {info.retrieved}" )
                        if info.retrieved != info.expected:
                            msg.append( f'result mismatch, expected {info.expected}, got {info.retrieved}' )

                        else:
                            self.Status = TaskStatus.OK

                    elif resultType == 'rows':
                        if not isinstance( info.expected, list ):
                            raise ValueError( f"Incorrect expected" )

                        info.retrieved = cursor.fetchall()
                        if info.recordcount == -1:  # SQLite3 doesn't set the 'cursor.reccount'
                            info.recordcount = len( info.retrieved )

                        errors = 0
                        for row, (cfgRecord, dbRecord) in enumerate( zip_longest( info.expected, info.retrieved ) ):
                            if isinstance( cfgRecord, dict ) and isinstance( dbRecord, dict ):
                                if not compare_dict( cfgRecord, dbRecord ):
                                    msg.append( f"{row} did not match the values" )
                                    errors += 1

                            elif isinstance( cfgRecord, dict ) and isinstance( dbRecord, (list, tuple) ):
                                for col, (cfgValue, dbValue) in enumerate( zip_longest( cfgRecord.values(), dbRecord ) ):
                                    if cfgValue != dbValue:
                                        errors += 1
                                        msg.append( f"Record {row + 1} don't match in column {col + 1} '{cfgValue}' != {dbValue}" ),

                            elif isinstance( cfgRecord, (list, tuple) ) and isinstance( dbRecord, dict ):
                                for col, (cfgValue, dbValue) in enumerate( zip_longest( cfgRecord, dbRecord.values() ) ):
                                    if cfgValue != dbValue:
                                        errors += 1
                                        msg.append( f"Record {row + 1} don't match in column {col + 1} '{cfgValue}' != {dbValue}" ),
                                        break

                            elif isinstance( cfgRecord, (list, tuple) ) and isinstance( dbRecord, (list, tuple) ):
                                for col, (cfgValue, dbValue) in enumerate( zip_longest( cfgRecord, dbRecord ) ):
                                    if cfgValue != dbValue:
                                        errors += 1
                                        msg.append( f"Record {row + 1} don't match in column {col + 1} '{cfgValue}' != {dbValue}" ),

                            else:
                                raise ValueError( "Invalid result configuration" )

                    if errors == 0:
                        self.Status = TaskStatus.OK
                        msg.append( "Records did match" )

                    self.Message = '\n'.join( msg )

        except ValueError as exc:
            self.Message = f"{exc}"

        except self.__sqlError as exc:
            self.Message = f"{exc}"

        except Exception as exc:
            self.Status = TaskStatus.FAILED
            self.log.exception( f"During SQL { self.Config.get( 'url' ) }" )
            self.setExceptionData( exc, traceback.extract_stack() )

        return self.Status