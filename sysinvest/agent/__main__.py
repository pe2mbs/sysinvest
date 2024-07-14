#
#   sysinvest:agent - Python system monitor and investigation utility
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
import platform
import sys
from datetime import datetime, timezone
from time import sleep
import getopt
import sysinvest.common.api as API
import sysinvest.version as version
from sysinvest.common.configuration import ConfigLoader
from sysinvest.common.interfaces import AgentRequest
from sysinvest.common.monitor import Monitor, AbstractForwarder
from sysinvest.common.plugin_agent import MonitorPluginAgent
import requests
import orjson
import logging


logger = logging.getLogger( 'agent' )

class Forwarder( AbstractForwarder ):
    def put( self, plugin: MonitorPluginAgent ):
        logger.info( repr( plugin.serverData ) )
        if plugin.serverData is None:
            class_name = None

        elif isinstance( plugin.serverData, list ) and len( plugin.serverData ) > 0:
            class_name = plugin.serverData[ 0 ].__class__.__name__

        else:
            class_name = plugin.serverData.__class__.__name__

        req = AgentRequest( timestamp = datetime.utcnow().replace(tzinfo = timezone.utc),
                            source = plugin.Name,
                            result = plugin.Status,
                            details = plugin.serverData,
                            message = plugin.Message,
                            class_name = class_name,
                            hostname = platform.node(),
                            version = version.version,
                            release = version.date )
        headers = { "Content-Type": "application/json" }
        try:
            print( f"{ orjson.dumps( req.dict(), option = orjson.OPT_INDENT_2 ).decode('utf-8') }" )
            r = requests.post( 'http://localhost:5000/api/agent', data = orjson.dumps( req.dict() ), headers = headers )
            logger.info( f"STATUS {r.status_code} - {r.content}" )

        except requests.exceptions.ConnectionError:
            logger.warning( "Server seems to be down" )

        return


def banner():
    print( f"""{version.package} {version.description}, version {version.version} date {version.date}
{version.copyright}""" )
    return


def usage():
    print( """Syntax:
    python -m si-agent [options] [taskfilename-1] [...] [taskfilename-X]

Example:
    python -m sysinvest.agent -c main-config.yaml tasks.conf

Options:
    -h/--help           This halp information
    -c/--config         generic configuration file
    -v                  verbose output

""" )


def main():
    banner()
    try:
        opts, args = getopt.getopt( sys.argv[ 1: ], "hc:v", [ "help", "config=" ] )

    except getopt.GetoptError as err:
        # print help information and exit:
        print( err )  # will print something like "option -a not recognized"
        usage()
        sys.exit( 2 )

    config = "config.conf"
    API.verbose = False
    for o, a in opts:
        if o == "-v":
            API.verbose = True

        elif o in ("-h", "--help"):
            usage()
            sys.exit()

        elif o in ("-c", "--config"):
            config = a

        else:
            assert False, "unhandled option"

    configuration = ConfigLoader( config, *args )
    while configuration.isLoading:
        sleep( 1 )

    print( "Starting the main loop" )
    processMonitor = Monitor( configuration, Forwarder() )
    processMonitor.run()
    return


if __name__ == '__main__':
    main()
