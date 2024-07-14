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
from dateutil import parser
from datetime import datetime
import enum

from sysinvest.common.interfaces import TaskStatus


class MonitorTaskStatus( enum.Enum ):
    IDLE        = 0
    COLLECTING  = 1
    WARNING     = 1
    FAILED      = 2




class PluginBase( object ):
    def __init__( self, config: dict, parent = None ):
        self.__cfg          = config
        self.__parent       = parent
        self.__configIndex  = 0
        self.__configDateTime = None
        self.__serverData   = {}
        self.__status       = TaskStatus.COLLECTING
        self.__message      = ''
        return

    def configure( self, config: dict ) -> None:
        self.__cfg = config
        return

    @property
    def ConfigIndex( self ) -> int:
        return self.__configIndex

    @ConfigIndex.setter
    def ConfigIndex( self, value: int ):
        self.__configIndex = value
        return

    @property
    def ConfigDateTime(self) -> datetime:
        return self.__configDateTime

    def ConfigDateTimeStr( self, fmt = "%Y-%m-%d - %H:%M:%S" ):
        return self.__configDateTime.strftime( fmt )

    @ConfigDateTime.setter
    def ConfigDateTime(self, value: t.Union[datetime,str,int]):
        if isinstance( value, datetime ):
            self.__configDateTime = value

        elif isinstance( value, int ):
            self.__configDateTime = datetime.fromtimestamp( value )

        elif isinstance( value, str ):
            self.__configDateTime = parser.parse( value )

        return

    @property
    def Parent( self ) -> t.Union[ 'MonitorPlugin','ReportPlugin' ]:
        return self.__parent

    @property
    def Config( self ) -> dict:
        return self.__cfg

    def __getitem__(self, item):
        if item in self.__cfg:
            return self.__cfg[ item ]

        raise

    def execute( self ) -> TaskStatus:
        return TaskStatus.COLLECTING

    @property
    def serverData( self ) -> t.Any:
        return self.__serverData

    def setServerData( self, obj ):
        self.__serverData = obj
        return

    @property
    def Status( self ) -> TaskStatus:
        return self.__status

    @Status.setter
    def Status( self, status: TaskStatus ):
        self.__status = status
        return

    @property
    def Message( self ) -> str:
        return self.__message

    @Message.setter
    def Message( self, msg: str ):
        self.__message = msg
        return

