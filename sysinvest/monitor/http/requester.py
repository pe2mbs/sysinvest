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
from sysinvest.common.plugin import MonitorPlugin, PluginResult
try:
    import requests

except:
    requests = None


def doRequest( plugin: MonitorPlugin, task_result, url, **kwargs ):
    r = requests.request( plugin.Attributes.get( 'method', 'GET' ).upper(), url, **kwargs )
    task_result.update( False, "Result code did not match" )
    result_code = plugin.Attributes.get( 'status_code', 200 )
    if r.status_code == result_code:
        content = plugin.Attributes.get( 'content' )
        plugin.log.info( r.content )
        if content is not None:
            if r.content != content:
                task_result.update( False, "Result code did match, but content failed" )

            else:
                task_result.update( True, "Result code did match and content" )

        else:
            task_result.update( True, "Result code did match" )

    else:
        task_result.update( True, f"Result code did match: {r.status_code} expected: {result_code}" )

    return