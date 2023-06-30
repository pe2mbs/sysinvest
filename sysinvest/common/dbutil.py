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
from urllib.parse import urlparse
from itertools import zip_longest
from sysinvest.common.plugin.monitor import MonitorPlugin


class SqlMonitorPlugin( MonitorPlugin ):
    def __init__( self, parent, obj: dict, allowed_schemes = None ):
        super().__init__( parent, obj )
        self.__allowed_schemes = allowed_schemes
        self.__host = None
        self.__port = None
        self.__username = None
        self.__password = None
        self.__database = None
        return

    @property
    def AllowedSchemes( self ):
        return self.__allowed_schemes

    @property
    def Host( self ):
        return self.__host

    @property
    def Port( self ):
        return self.__port

    @property
    def Username(self):
        return self.__username

    @property
    def Password(self):
        return self.__password

    @property
    def Database(self):
        return self.__database

    def getDatabaseConfig( self ):
        url = self.Attributes.get('url')
        if isinstance(url, str):
            o = urlparse(url)
            if isinstance( self.__allowed_schemes, (list,tuple)) and o.scheme not in self.__allowed_schemes:
                raise ValueError( f"scheme '{o.scheme}'  did not match the allowed schemes {self.__allowed_schemes}" )

            self.__host = o.hostname
            self.__port = o.port if isinstance(o.port, int) else 3306
            self.__username = o.username
            self.__password = o.password
            self.__database = o.path[1:]

        else:
            self.__host = self.Attributes.get('host')
            self.__port = self.Attributes.get('port', 3306)
            self.__username = self.Attributes.get('username')
            self.__password = self.Attributes.get('password')
            self.__database = self.Attributes.get('database')

        if self.__host is None:
            raise ValueError("'host' or 'url' not set")

        if self.__username is None:
            raise ValueError("'username' not set")

        if self.__password is None:
            raise ValueError("'password' not set")

        if self.__database is None:
            raise ValueError("'database' not set")

        return

    def verifyDatabaseResult( self, cursor, task_result ):
        resultType = self.Attributes.get('type', 'rows')
        expected = self.Attributes.get('result')
        if resultType == 'scalar':
            result = cursor.fetchone()
            self.log.info(f"Query result : {result}")
            if result[0] != expected:
                task_result.update(False, f'result mismatch, expected {expected}, got {result[0]}')

        elif resultType == 'rows':
            for row, (cfgRecord, dbRecord) in enumerate(zip_longest(expected, cursor.fetchall())):
                if isinstance(cfgRecord, dict):
                    # Do the compare
                    for col, ((cfgField, cfgValue), (dbField, dbValue)) in enumerate(
                            zip_longest(cfgRecord.items(), dbRecord.items())):
                        if cfgField != dbField:
                            raise ValueError(
                                f"Invalid result configuration, in row {row} for field {cfgField}/{dbField}")

                        elif cfgValue != dbValue:
                            task_result.update(False,
                                               f"Record {row + 1} don't match in column {col + 1} plugin '{self.Name}'",
                                               dbRecord=dbRecord,
                                               cfgRecord=cfgRecord,
                                               dbField=dbField,
                                               cfgField=cfgField)
                            break

                elif isinstance(cfgRecord, (list, tuple)):
                    for col, (cfgValue, dbValue) in enumerate(zip_longest(cfgRecord, dbRecord.values())):
                        if cfgValue != dbValue:
                            task_result.update(False,
                                               f"Record {row + 1} don't match in column {col + 1} plugin '{self.Name}'",
                                               dbRecord=dbRecord,
                                               cfgRecord=list(dbRecord.values()),
                                               cfgValue=cfgValue,
                                               dbValue=dbValue)
                            break

                else:
                    raise ValueError("Invalid result configuration")

                if not task_result.Result:
                    break

            if task_result.Result:
                task_result.update(True, f'result matched the expected result {expected}')

        else:
            raise ValueError(f"Unknow rerult type: {resultType}")

        return task_result.Result