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
import yaml
import logging
import logging.config
from common.monitor import Monitor
from common.collector import Collector
from queue import Queue
import common.api as API


def main():
    with open( "config.conf", "r" ) as stream:
        config = yaml.load( stream, Loader = yaml.Loader )

    log_cfg = config.get( 'logging' )
    if log_cfg:
        logging.config.dictConfig( log_cfg )

    API.QUEUE           = Queue()
    API.verbose         = True
    processMonitor = Monitor( config )
    collector = Collector( config )
    collector.start()
    processMonitor.run()
    return


if __name__ == '__main__':
    main()
