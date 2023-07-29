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
import traceback
import sysinvest.common.plugin.constants as const
import sysinvest.monitor.http.requester as req
import sysinvest.common.api as API


class Http( MonitorPlugin ):
    def execute( self ):
        super().execute()
        kwargs = self.Attributes.get( 'parameters', {} )
        if 'username' in kwargs:
            # JNeed to translate the username/password
            auth = ( kwargs[ 'username' ], kwargs[ 'password' ] )
            del kwargs[ 'username' ]
            del kwargs[ 'password' ]
            kwargs[ 'auth' ] = auth

        url = self.Attributes.get( 'url', 'http://localhost' )
        if req.requests is not None:
            try:
                req.doRequest( self, self, url, **kwargs )

            except Exception as exc:
                self.update( False, str(exc), { const.C_EXCEPTION: exc, const.C_TRACEBACK: traceback.format_exc() },
                                       filename = url )

        else:
            self.update( False, "Python 'requests' package not installed",
                                   { const.C_EXCEPTION: "ModuleNotFoundError: No module named 'requests'",
                                     const.C_TRACEBACK: traceback.format_stack() },
                                   filename = url )

        API.QUEUE.put( self )
        return