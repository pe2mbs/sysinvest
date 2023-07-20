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
from datetime import datetime, timedelta
import logging
import importlib
from threading import Event
from sysinvest.common.plugin import MonitorPlugin
import sysinvest.common.api as API
from sysinvest.common.configuration import ConfigLoader


class Monitor( list ):
    def __init__( self, config_class: ConfigLoader ):
        super().__init__()
        self.log            = logging.getLogger( 'monitor' )
        self.__p            = psutil.Process( os.getpid() )
        self.__event        = Event()
        self.__running      = False
        self.__passes       = 0
        self.__cfgClass     = config_class
        self.__cfgIndex     = 0
        self.loadModules()
        return

    def loadModules( self ):
        self.__cfgIndex += 1
        for obj in self.__cfgClass.Configuration[ 'objects' ]:
            try:
                module = obj[ 'module' ]
                mod = None
                self.log.info( f'Loading monitor: {obj}')
                for mod_path in ( '', 'sysinvest.', 'sysinvest.monitor.' ):
                    try:
                        mod = importlib.import_module( f'{mod_path}{module}' )
                        getattr(mod, 'CLASS_NAME')
                        _class = getattr(mod, getattr(mod, 'CLASS_NAME'))
                        executor = _class( self, obj )
                        if executor not in self:
                            self.append( executor )

                        executor.ConfigIndex = self.__cfgIndex
                        executor.ConfigDateTime = datetime.now()
                        break

                    except:
                        pass

                if mod is None:
                    self.log.error( f"Could not load {obj}")

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
        startTime = datetime.fromtimestamp( self.__p.create_time() )
        upTime = datetime.now() - startTime
        return {
            'since':  startTime.strftime( '%Y-%m-%d %H:%M:%S' ),
            'uptime': f"{upTime.days} - {str(timedelta( seconds = upTime.seconds ))}",
            'passes': self.__passes,
            'tasks':  len( self )
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
                    if not task.Enabled:
                        continue

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
                    self.__event.wait( sleepTime )

                if len( self ) < len( self.__cfgClass.Configuration[ 'objects' ] ):
                    # We need to load more modules
                    self.loadModules()

        except:
            raise

        finally:
            # Stop all threaded tasks
            for task in self:
                if hasattr( task, 'stop' ):
                    task.stop()

        return
