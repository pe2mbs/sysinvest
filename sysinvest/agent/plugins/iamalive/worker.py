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
import os
import traceback
import psutil
from sysinvest.common.checkpid import updateProcessData
from sysinvest.common.interfaces import ProcessData, TaskStatus, ExceptionData
from sysinvest.common.plugin_agent import MonitorPluginAgent
from datetime import datetime, timezone
import pytz


class IamAliveAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj: dict ):
        super().__init__( parent, obj )
        self.__pid = os.getpid()
        self.Status = TaskStatus.COLLECTING
        self.setServerData( ProcessData( pid = self.__pid,
                                         since = datetime.now( pytz.timezone('Europe/Amsterdam') ),
                                         lasttime = datetime.now( pytz.timezone('Europe/Amsterdam') ),
                                         tasks = len( parent ) ) )
        self.runOnStartup()
        return

    def execute( self ) -> TaskStatus:
        super().execute()
        self.log.info( "Updating" )
        self.serverData.tasks = len( self.Parent )
        self.serverData.lasttime = datetime.now( pytz.timezone('Europe/Amsterdam') )
        try:
            process = psutil.Process( self.__pid )
            updateProcessData( process, self.serverData )
            self.Message = 'Running'
            self.Status = TaskStatus.OK

        except psutil.NoSuchProcess as exc:
            self.Status = TaskStatus.FAILED
            self.Message = 'NoSuchProcesss'
            self.setExceptionData( exc, traceback.extract_stack() )

        except Exception as exc:
            self.log.exception( "During lookup process" )
            self.Message = str( exc )
            self.Status = TaskStatus.FAILED
            self.setExceptionData( exc, traceback.extract_stack() )

        return self.Status
