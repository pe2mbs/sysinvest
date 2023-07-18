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
import pycron
import psutil
import os
import time
import datetime
import logging
import importlib
from threading import Event
from sysinvest.common.plugin import MonitorPlugin
import sysinvest.common.api as API


class Monitor( list ):
    def __init__( self, config ):
        super().__init__()
        self.log            = logging.getLogger( 'monitor' )
        self.__p            = psutil.Process(os.getpid())
        self.__event        = Event()
        self.__running      = False
        self.__passes       = 0
        self.__cfg          = config
        for obj in config[ 'objects' ]:
            if not obj.get('enabled', False ):
                continue

            try:
                module = obj[ 'module' ]
                self.log.info( f'Loading monitor: {obj}')
                if '.' not in module:
                    module = f'sysinvest.monitor.{module}'

                elif module.startswith( "os." ):
                    module = f'sysinvest.monitor.{module}'

                elif module.startswith( "monitor." ):
                    module = f'sysinvest.{module}'

                mod = importlib.import_module( module )
                getattr( mod, 'CLASS_NAME' )
                _class = getattr( mod, getattr( mod, 'CLASS_NAME' ) )
                executor = _class( self, obj )
                self.append( executor )

            except Exception:
                self.log.exception( f"During module load: {obj}" )

        return

    def addToQueue( self, result ):
        self.log.info( f"Queue add {API.QUEUE.qsize()}" )
        API.QUEUE.put_nowait( result )
        self.log.info( f"Queue: {API.QUEUE.qsize()} Done" )
        return

    @property
    def Name( self ):
        return "ProcessMonitor"

    @property
    def Attributes( self ):
        return {}

    def info( self ) -> dict:
        startTime = datetime.datetime.fromtimestamp( self.__p.create_time() )
        upTime = datetime.datetime.now() - startTime
        return {
            'since': startTime.strftime( '%Y-%m-%d %H:%M:%S' ),
            'uptime': f"{upTime.days} - {str(datetime.timedelta( seconds = upTime.seconds ))}",
            'passes': self.__passes,
            'tasks': len( self )
        }

    def stop( self ):
        self.__event.set()
        return

    def run( self ):
        isStarting = True
        try:
            while not self.__event.is_set():
                self.__passes += 1
                start = int( time.time() )
                for task in self:
                    task: MonitorPlugin
                    if not pycron.is_now( task.Cron ) and not isStarting:
                        continue

                    self.log.info( f"{task.Name} is being started" )
                    task.execute()
                    self.log.info( f"{task.Name} is finished" )

                isStarting = False
                # Loop time should be about a minute, sleep the remaining time
                sleepTime = 60 - ( int( time.time() ) - start )
                self.log.info( f"Sleep time: {sleepTime}" )
                if sleepTime > 0:
                    time.sleep( sleepTime)

        except:
            raise

        finally:
            # Stop all threaded tasks
            for task in self:
                if hasattr( task, 'stop' ):
                    task.stop()

        return
