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
import shutil
from sysinvest.common.plugin import MonitorPlugin
import sysinvest.common.api as API
from sysinvest.common.bytesizes import shorthand2sizeof, sizeof2shorthand


def convertByteSize( size ):
    if isinstance( size, str ):
        size = shorthand2sizeof( size.replace(' ', '' ) )

    return size


def checkFileSystem( fs, result, messages ):
    filesystem = fs.get( 'filesystem' )
    if not os.path.exists( filesystem ):
        result.append( f"{filesystem} doesn't exists" )

    freespace = convertByteSize( fs.get( 'freespace' ) )
    total, used, free = shutil.disk_usage(filesystem)
    if freespace is not None and freespace > free:
        result.append( f"{filesystem} freespace {sizeof2shorthand(free)} too less should be at least {sizeof2shorthand(freespace)}")

    else:
        messages.append( f"{filesystem} freespace {sizeof2shorthand(free)}" )

    totalspace = convertByteSize( fs.get( 'totalspace' ) )
    if totalspace is not None and totalspace > total:
        result.append( f"{filesystem} total disk space {sizeof2shorthand(total)} too less should be at least {sizeof2shorthand(totalspace)}")

    return


class FileSystemMonitor( MonitorPlugin ):
    def execute( self ) -> None:
        super().execute()
        filesystem = self.Attributes.get( 'filesystem' )
        self.log.info( f"Checking filesystem: {filesystem}" )
        try:
            result = []
            messages = []
            if isinstance( filesystem, list ):
                for fs in filesystem:
                    checkFileSystem( fs, result, messages )

            elif isinstance( filesystem, dict ):
                checkFileSystem( filesystem, result, messages )

            else:
                raise ValueError( "'filesystem' incorrect set or missing" )

            if len( result ) == 0:
                self.update(True, "Filesystem OK: \n{}".format( "\n".join( messages ) ) )

            else:
                self.update(False, "Filesystem NOK: \n{}".format( "\n".join( result ) ) )

        except ValueError as exc:
            self.update(False, f"{exc}")

        except Exception as exc:
            self.log.exception("in FileSystemMonitor")
            self.update(False, f"{exc}")

        API.QUEUE.put(self)
        return
