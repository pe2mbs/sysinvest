#
#   sysinvest - Python system monitor and investigation utility
#   Copyright (C) 2022-2024 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
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
import platform
from sysinvest.common.plugin import MonitorPlugin, PluginResult
import sysinvest.common.api as API
from mako.template import Template


class EnvironmentMonitor( MonitorPlugin ):
    def execute( self ) -> bool:
        super().execute()
        errors = []
        messages = []
        task_result = PluginResult(self)
        self.log.info(f"Checking { platform.uname() } OS environment: { os.environ }")
        try:
            if self.Attributes.get( 'machine', platform.machine() ) != platform.machine():
                errors.append( f"Machine detected: {platform.machine()}" )

            if self.Attributes.get( 'version', platform.version() ) != platform.version():
                errors.append( f"Version detected: {platform.version()}" )

            if self.Attributes.get( 'platform', platform.platform() ) != platform.platform():
                errors.append( f"Platform detected: {platform.platform()}" )

            if self.Attributes.get( 'processor', platform.processor() ) != platform.processor():
                errors.append( f"Processor detected: {platform.processor()}" )

            if len(errors) == 0:
                uname = platform.uname()
                uname_result = " ".join( [ "{}: {}".format( field, getattr( uname, field ) ) for field in (x for x in dir(uname) if "_" not in x and not callable(getattr(uname, x))) ] )
                messages.append( f"Platform: {uname_result}")

            for variable in self.Attributes.get( 'variables', [] ):
                if variable not in os.environ:
                    errors.append(f"Variable '{variable}' not set in the environment")

                else:
                    messages.append(f"Variable '{variable}' contains { os.environ[ variable ] }")

            if len( errors ) == 0:
                task_result.update(True, "Environment OK:\n{}".format("\n".join(messages)) )

            else:
                task_result.update(False, "Environment NOK: \n{}\nOK:\n{}".format("\n".join(errors),"\n".join(messages)))

        except ValueError as exc:
            task_result.update(False, f"{exc}")

        except Exception as exc:
            self.log.exception("in EnvironmentMonitor")
            task_result.update(False, f"{exc}")

        API.QUEUE.put(task_result)
        return task_result.Result

