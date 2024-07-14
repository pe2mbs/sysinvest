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
import platform
import traceback
from sysinvest.common.interfaces import TaskStatus, EnvironmentData, EnvironmentVars
from sysinvest.common.plugin_agent import MonitorPluginAgent


class EnvironmentAgent( MonitorPluginAgent ):
    def execute( self ) -> TaskStatus:
        super().execute()
        self.Status = TaskStatus.FAILED
        errors = []
        self.log.info( f"Checking { platform.uname() } OS environment: { os.environ }" )
        try:
            uname = platform.uname()
            uname_str = f"{uname.system} {uname.node} {uname.release} {uname.version} {uname.machine} {uname.processor}"
            info = EnvironmentData( machine = platform.machine(), platform = platform.platform(),
                                    processor = platform.processor(), version = platform.version(),
                                    uname = uname_str )
            self.setServerData( info )
            if self.Config.get( 'machine', platform.machine() ) != info.machine:
                errors.append( f"Machine detected: {info.machine}" )

            if self.Config.get( 'version', platform.version() ) != info.version:
                errors.append( f"Version detected: {info.version}" )

            if self.Config.get( 'platform', platform.platform() ) != info.platform:
                errors.append( f"Platform detected: {info.platform}" )

            if self.Config.get( 'processor', platform.processor() ) != info.processor:
                errors.append( f"Processor detected: {info.processor}" )

            environment = []
            for variable, expected in self.Config.get( 'variables', {} ).items():
                if variable not in os.environ:
                    errors.append( f"Variable '{variable}' not set in the environment")

                else:
                    environment.append( EnvironmentVars( name = variable, value = os.environ[ variable ] ) )
                    if expected != os.environ[ variable ]:
                        errors.append( f"Variable {variable} has incorrect value {os.environ[ variable ]}, expected {expected} " )

            if len( environment ) > 0:
                info.environment = environment

            if len( errors ) == 0:
                self.Message = "Environment OK"
                self.Status = TaskStatus.OK

            else:
                self.Message = "\n".join( errors )

        except ValueError as exc:
            self.Message = f"{exc}"

        except Exception as exc:
            self.log.exception( f"During SQL { self.Config.get( 'url' ) }" )
            self.setExceptionData( exc, traceback.extract_stack() )

        return self.Status

