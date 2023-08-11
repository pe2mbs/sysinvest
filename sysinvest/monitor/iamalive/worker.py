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
from sysinvest.common.plugin import MonitorPlugin
import sysinvest.common.api as API


class AmiAlive( MonitorPlugin ):
    DEFAULT_TEMPLATE = """SysInvest infrastructure monitor daemon is alive, running since ${since}
Uptime ${uptime} with no. ${passes} passes, checking ${tasks} tasks
"""
    def __init__( self, parent, obj: dict ):
        super().__init__( parent, obj )
        self.runOnStartup()
        return

    def execute( self ):
        self.log.info("Updating")
        self.update( True, "Process active" )
        API.QUEUE.put( self )
        return
