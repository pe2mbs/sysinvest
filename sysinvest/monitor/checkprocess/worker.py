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
import traceback
from sysinvest.common.plugin import MonitorPlugin
import sysinvest.common.plugin.constants as const
import psutil
import sysinvest.common.api as API


class CheckProcess( MonitorPlugin ):
    DEFAULT_TEMPLATE = """${message}
    
"""
    def execute( self ) -> None:
        super().execute()
        try:
            result = None
            executable = self.Attributes.get( 'executable' )
            commandline = self.Attributes.get( 'commandline', [] )
            if isinstance( commandline, str ):
                commandline = commandline.split( ' ' )

            for proc in psutil.process_iter():
                try:
                    cmdline = proc.cmdline()
                    # self.log.info( "Process {}".format( " ".join( cmdline ) ) )
                    if len( cmdline ) > 0 and cmdline[0] == executable:
                        self.log.debug( f"executable found: {executable} ")
                        count = 0
                        for arg in commandline:
                            if arg in cmdline[1:]:
                                count += 1

                        if count == len(commandline):
                            result = ' '.join( commandline )
                            self.log.info( f"process found: {executable} {result}")
                            break

                except psutil.AccessDenied:
                    pass

                except Exception:
                    raise

            if result is None:
                result = ' '.join(commandline)
                self.log.warning( f"process NOT found: {executable} {result}" )
                self.update( False, f"Executable {executable} with command line '{result}' doesn't exist" )

            else:
                self.update( True, f"Executable {executable} with command line '{result}' exist" )

        except Exception as exc:
            self.log.exception( "During lookup process" )
            self.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() } )

        API.QUEUE.put( self )
        return
