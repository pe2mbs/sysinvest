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
import sys
import yaml
import getopt
import logging
import logging.config
from sysinvest.common.monitor import Monitor
from sysinvest.common.collector import Collector
from queue import Queue
import sysinvest.common.api as API
import sysinvest.version as version

def banner():
    print(f"""{version.package} {version.description}, version {version.version} date {version.date}
{version.copyright}""")
    return


def usage():
    print("""Syntax:
    python -m sysinvest [options] [taskfilename-1] [...] [taskfilename-X]

Example:
    python -m sysinvest -c main-config.yaml tasks.conf

Options:
    -h/--help           This halp information
    -c/--config         generic configuration file
    -v                  verbose output
    
""")


def main():
    banner()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:v", ["help", "config="])

    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

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

    with open( config, "r" ) as stream:
        config = yaml.load( stream, Loader = yaml.Loader )

    log_cfg = config.get( 'logging' )
    if log_cfg:
        logging.config.dictConfig( log_cfg )

    # Join the config files
    tasks = config.setdefault( 'objects', [] )
    for arg in args:
        if os.path.exists( arg ):
            with open(arg, "r") as stream:
                taskset = yaml.load(stream, Loader=yaml.Loader)

            for key, value in taskset.items():
                if key == 'objects':
                    tasks.extend( value )

                else:
                    config[ key ] = value

        else:
            raise FileNotFoundError( f"Could not load {arg}" )

    API.QUEUE           = Queue()
    processMonitor = Monitor( config )
    collector = Collector( config )
    collector.start()
    processMonitor.run()
    return


if __name__ == '__main__':
    main()
