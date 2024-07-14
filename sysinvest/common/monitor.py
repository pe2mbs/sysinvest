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
import logging
import importlib
from threading import Event
from sysinvest.common.interfaces import TaskStatus
from sysinvest.common.plugin_agent import MonitorPluginAgent
from sysinvest.common.watchdog import ProcessWatchdog
from sysinvest.common.configuration import ConfigLoader
from abc import ABC, abstractmethod


class AbstractForwarder( ABC ):
    @abstractmethod
    def put( self, plugin: MonitorPluginAgent ):
        raise NotImplemented()




class Monitor( list ):
    def __init__( self, config_class: ConfigLoader, forwarder: AbstractForwarder ):
        super().__init__()
        self.log            = logging.getLogger( 'monitor' )
        self.__p            = psutil.Process( os.getpid() )
        self.__event        = Event()
        self.__running      = False
        self.__passes       = 0
        self.__cfgClass     = config_class
        self.__cfgIndex     = 0
        self.__forwarder    = forwarder
        self.loadModules()
        return

    def loadModules( self ):
        self.__cfgIndex += 1
        for obj in self.__cfgClass.Configuration[ 'objects' ]:
            try:
                module = obj[ 'module' ]
                mod = None
                self.log.info( f'Loading monitor: {obj}')
                for mod_path in ( 'sysinvest.agent.plugins', 'sysinvest.plugins' ):
                    try:
                        mod = importlib.import_module( f'{mod_path}.{module}' )
                        getattr(mod, 'CLASS_NAME')
                        _class = getattr(mod, getattr(mod, 'CLASS_NAME'))
                        executor = _class( self, obj )
                        if not executor.Enabled:
                            self.log.warning( f"{ module } not enabled '{executor.Name}'" )
                            break

                        if executor not in self:
                            self.append( executor )

                        break

                    except ModuleNotFoundError:
                        self.log.error( f"{mod_path}.{module} was not found" )

                    except Exception:
                        self.log.exception( f"During loading of {module}" )
                        pass

            except Exception:
                self.log.exception( f"During module load: {obj}" )

        self.log.info( f"Modules loaded: { len( self ) }" )
        return

    @property
    def Name( self ):
        return "ProcessMonitor"

    @property
    def TaskCount( self ) -> int:
        return len( [ e for e in self if e.Enabled ] )

    def stop( self ):
        self.__event.set()
        return

    def run( self ):
        wd = ProcessWatchdog()
        isStarting = True
        self.log.info( f"No of tasks: { len( self ) }" )
        try:
            while not self.__event.is_set():
                wd.trigger()
                self.__passes += 1
                start = int( time.time() )
                for task in self:
                    task: MonitorPluginAgent
                    task.Passes = self.__passes
                    if not task.Enabled:
                        continue

                    if not isStarting and not pycron.is_now( task.Cron ):
                        continue

                    self.log.info( f"{task.Name} is being started" )
                    if task.execute() == TaskStatus.OK:
                        task.resetHits()

                    self.__forwarder.put( task )
                    self.log.info( f"{task.Name} is finished" )

                isStarting = False
                # Loop time should be about a minute, sleep the remaining time
                sleepTime = 60 - ( int( time.time() ) - start )
                self.log.info( f"Sleep time: {sleepTime}" )
                if sleepTime > 0:
                    self.__event.wait( sleepTime )

        except:
            raise

        finally:
            # Stop all threaded tasks
            for task in self:
                if hasattr( task, 'stop' ):
                    task.stop()

        return
