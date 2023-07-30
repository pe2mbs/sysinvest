from typing import List, Tuple
from threading import Thread, Event
from datetime import datetime
import os
import copy
import yaml
import logging
import logging.config

class InvalidConfig( Exception ): pass


class ConfigLoader( Thread ):
    def __init__(self, wait_time: int = 60, *args, **kwargs ):
        super().__init__()
        self.log                        = logging.getLogger( 'monitor' )
        self.__configuration            = {}
        self.__event                    = Event()
        self.__lastTimeStamp            = 0
        self.__updateIndex              = 0
        self.__loadingEvent             = Event()
        self.__loadingEvent.set()
        self.__waitTime                 = wait_time
        # This starts the thread and loads the configuration
        self.start()
        return

    def stop(self):
        self.__event.set()
        return

    def checkForReload( self ) -> bool:
        raise NotImplemented()

    def run( self ):
        while not self.__event.is_set():
            if self.checkForReload():
                self.reload()

            # Here we wait for a minute of when the event is set
            self.__event.wait( self.__waitTime )

        return

    def reload(self):
        raise NotImplemented()

    @property
    def isLoading(self):
        return self.__loadingEvent.is_set()

    def whileIsLoading( self ):
        while self.__loadingEvent.is_set():
            self.__loadingEvent.wait( 5 )

        return

    def __updateObjects(self, items, master_config):
        for item in items:
            found = False
            for master in master_config:
                if master.get('name') == item.get('name'):
                    found = True
                    for ikey, ivalue in item.items():
                        master[ ikey ] = ivalue

                    master[ 'index' ] = self.__updateIndex
                    master[ 'update_dt' ] = datetime.now()

            if not found:
                item[ 'index' ] = self.__updateIndex
                item[ 'update_dt' ] = datetime.now()
                master_config.append(copy.copy(item))


        return

    @property
    def Configuration( self ) -> dict:
        return self.__configuration


