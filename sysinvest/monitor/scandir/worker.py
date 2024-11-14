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
import json
import humanfriendly
from sysinvest.common.plugin import MonitorPlugin, PluginResult
import sysinvest.common.api as API
from mako.template import Template


class ScanDirMonitor( MonitorPlugin ):
    def execute( self ) -> bool:
        super().execute()
        task_result = PluginResult( self )
        folder = self.Attributes.get('folder' )
        max_size = self.Attributes.get( 'max-size', "2GB" )
        if isinstance( max_size, (int, float) ):
            max_size = int( max_size )

        elif isinstance( max_size, str ):
            max_size = humanfriendly.parse_size( max_size )

        self.log.info(f"Checking { folder }")
        result = self.diskusage_folders( folder, max_size )
        self.log.info( json.dumps( result, indent = 4 ) )
        messages = []
        for user, used_size in result.items():
            fullpath = os.path.join( folder, user )
            size = humanfriendly.format_size( used_size )
            # messages.append( f'{ size } in use by "{ fullpath }"' )
            messages.append( f'<li><span style="color: red">{ size }</span> in use by { fullpath }</li>' )

        if len( messages ) == 0:
            task_result.update( True, "No folders exceed usage space" )

        else:
            tekst = ''.join( messages )
            self.log.warning(f"The following folders exceed usage space:\n{ json.dumps( result, indent = 4 ) }")
            task_result.update( False, f"\nThe following folders exceed usage space:\n<ul>{ tekst }</ul>"  )

        API.QUEUE.put( task_result )
        return task_result.Result

    def scan_folder_size( self, folder: str) -> int:
        size = 0
        try:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isdir(filepath):
                    size += self.scan_folder_size(filepath)

                else:
                    size += os.stat(filepath).st_size

        except OSError:
            pass

        return size

    def diskusage_folders( self, root_folder: str, excess: int = 0) -> dict:
        total = {}
        for filename in os.listdir(root_folder):
            filepath = os.path.join(root_folder, filename)
            if os.path.isdir(filepath):
                self.log.info(f"Investigating: {filepath}" )
                size = self.scan_folder_size(filepath)
                if size > excess:
                    total[filename] = size

                self.log.info(f"Found: {filepath} {humanfriendly.format_size(size)} inuse")

        return total