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
import os
import psutil
import shutil
import traceback
from pydantic import BaseModel
from sysinvest.common.interfaces import TaskStatus
from sysinvest.common.plugin_agent import MonitorPluginAgent
from sysinvest.common.bytesizes import shorthand2sizeof, sizeof2shorthand


class IMonitorDevices( BaseModel ):
    device:     str
    mountpoint: t.Optional[ str ] = None
    fstype:     t.Optional[ str ] = None
    free_space: t.Optional[ t.Union[ str, int ] ] = None


class IMonitorDeviceInfo( BaseModel ):
    mountpoint:     str
    total:          int
    used:           int
    free:           int
    free_percent:   t.Optional[ float ] = None
    free_valid:     t.Optional[ bool ] = None


class InvalidFreeSpace( Exception ):
    pass


class FileSystemAgent( MonitorPluginAgent ):
    def checkFileSystem( self, partition: IMonitorDevices ):
        total, used, free = shutil.disk_usage( partition.mountpoint )
        info = IMonitorDeviceInfo( mountpoint = partition.mountpoint, total = total, used = used, free = free )
        if isinstance( partition.free_space, str ):
            if partition.free_space.endswith( '%' ):
                free_space_percent = int( partition.free_space[ :-1 ] )
                freespace = int((total / 100) * free_space_percent)

            else:
                freespace = int( partition.free_space )

        elif isinstance( partition.free_space, int ):
            freespace = int( partition.free_space )

        elif partition.free_space is None:
            info.free_percent = ((total-used)/total) * 100
            info.free_valid = True
            return info

        else:
            raise InvalidFreeSpace()

        info.free_percent = ((total-used)/total) * 100
        print( info.free, freespace, total-used )
        info.free_valid = info.free > (total-freespace)
        return info


    def execute( self ) -> TaskStatus:
        super().execute()
        self.Status = TaskStatus.FAILED
        partitions = [ IMonitorDevices( **dev ) for dev in self.Config.get( 'partitions', [] ) ]
        msg = []
        try:
            result = []
            for partition in psutil.disk_partitions():
                for monitor_partition in partitions:
                    if partition.device != monitor_partition.device:
                        continue

                    if isinstance( monitor_partition.mountpoint, str ):
                        if monitor_partition.mountpoint != partition.mountpoint:
                            msg.append( f"{ partition.device } has invalid mounting pount { partition.mountpoint } expected { monitor_partition.mountpoint }" )

                    if isinstance( monitor_partition.fstype, str ):
                        if monitor_partition.fstype != partition.fstype:
                            msg.append( f"{ partition.device } has invalid file-system { partition.fstype } expected { monitor_partition.fstype }" )

                    try:
                        info = self.checkFileSystem( monitor_partition )
                        result.append( info )
                        if info.free_valid:
                            self.Status = TaskStatus.OK
                            msg.append( f"{ info.mountpoint } total { sizeof2shorthand( info.total ) } used { sizeof2shorthand( info.used ) } free { sizeof2shorthand( info.free ) } ({info.free_percent:.2f}%)" )

                        else:
                            msg.append( f"{ info.mountpoint } has too less space available { sizeof2shorthand( info.free ) } = { info.free_percent }" )

                    except InvalidFreeSpace:
                        msg.append( f"Freespace parameter is invalid for { monitor_partition.mountpoint }" )

                    except Exception:
                        raise

            self.Message = "\n".join( msg )
            self.setServerData( result )

        except Exception as exc:
            self.log.exception( "in FileSystemAgent" )
            self.setExceptionData( exc, traceback.extract_stack() )

        return self.Status
