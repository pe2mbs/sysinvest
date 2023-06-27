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
import time
import logging
from common.plugin.result import PluginResult
import importlib
import _queue
import threading
import ctypes
import common.api as API

def _async_raise( tid, excobj ):
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc( tid, ctypes.py_object( excobj ) )
    if res == 0:
        raise ValueError( "nonexistent thread id" )

    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError( "PyThreadState_SetAsyncExc failed" )

    return

class Collector( threading.Thread ):
    def __init__( self, config: dict ):
        super().__init__()
        self.__stop = threading.Event()
        self.__classes = []
        self.__cfg = config.get( 'collector', {} )
        self.__messageCount = 0
        self.__lastTime = time.time()
        self.log = logging.getLogger( 'collector' )
        for forward in self.__cfg.get( 'forward', [] ):
            for mod_name in self.__cfg.get( 'modules', [] ):
                if not mod_name.endswith( forward ):
                    continue

                try:
                    self.log.info( f'Loading module: {mod_name}')
                    mod = importlib.import_module( mod_name )
                    _class = getattr( mod, getattr( mod, 'REPORT_CLASS' ) )
                    self.__classes.append( _class( self.__cfg ) )

                except Exception:
                    self.log.exception( f"Probem initializing collector module: {mod_name}" )

        return

    def raise_exc( self, excobj ):
        assert self.isAlive(), "thread must be started"
        for tid, tobj in threading._active.items():         # noqa
            if tobj is self:
                _async_raise( tid, excobj )
                return

        # the thread was alive when we entered the loop, but was not found
        # in the dict, hence it must have been already terminated. should we raise
        # an exception here? silently ignore?
        return

    def terminate(self):
        # must raise the SystemExit type, instead of a SystemExit() instance
        # due to a bug in PyThreadState_SetAsyncExc
        self.raise_exc( SystemExit )
        return

    def stop( self ):
        self.__stop.set()
        return

    def stopped(self):
        return self.__stop.is_set()

    def run( self ):
        self.__running = True
        while not self.stopped():
            try:
                item = API.QUEUE.get_nowait()
                self.log.info( f"Dequeue: {item}"  )
                self.notify( item )
                API.QUEUE.task_done()

            except _queue.Empty:
                pass

            except Exception as exc:
                self.log.exception( f"Exception: {exc}" )

            if API.QUEUE.qsize() > 0:
                self.log.info( f"Queue items: {API.QUEUE.qsize()}" )
                continue

            time.sleep( 5 )

        return

    def notify( self, event: PluginResult ):
        self.log.info( f"notify: {event}" )
        if not event.Result and not event.Plugin.Priority:
            # Count the failed messages
            self.__messageCount += 1

        for _class in self.__classes:
            self.log.info( f"notify: {_class}" )
            _class.notify( event )
            if event.Plugin.Priority:
                _class.publish()

        return

    def publish( self ):
        # For publishing we need to check the threshold values
        doPublish = False
        thresholds = self.__cfg.get( 'thresholds', {} )
        if self.__messageCount >= thresholds.get( 'messages', 1 ):
            doPublish = True

        if time.time() - self.__lastTime > thresholds.get( 'time', 60 ):
            doPublish = True

        if not doPublish:
            return

        for _class in self.__classes:
            _class.publish()

        self.__lastTime = time.time()
        self.__messageCount = 0
        return
