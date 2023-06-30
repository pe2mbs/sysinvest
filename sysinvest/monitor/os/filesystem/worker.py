import os
import shutil
from sysinvest.common.plugin import MonitorPlugin, PluginResult
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
        task_result = PluginResult(self)
        filesystem = self.Attributes.get( 'filesystem' )
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
                task_result.update(True, "Filesystem OK: \n{}".format( "\n".join( messages ) ) )

            else:
                task_result.update(False, "Filesystem NOK: \n{}".format( "\n".join( result ) ) )

        except ValueError as exc:
            task_result.update(False, f"{exc}")

        except Exception as exc:
            self.log.exception("in FileSystemMonitor")
            task_result.update(False, f"{exc}")

        API.QUEUE.put(task_result)
        return
