from typing import List, Tuple
from threading import Thread, Event
from datetime import datetime
import os
import copy
import yaml
import logging
import logging.config


class ConfigLoader( Thread ):
    def __init__(self, master_config: str, *option_config: Tuple[str], **kwargs):
        super().__init__()
        self.log                        = logging.getLogger( 'monitor' )
        self.__masterConfig: str        = master_config
        self.__optionConfig: List[str]  = list( option_config )
        self.__configuration            = {}
        self.__event                    = Event()
        self.__lastTimeStamp            = 0
        self.__updateIndex              = 0
        self.__loading                  = True
        # This starts the thread and loads the configuration
        self.start()
        return

    def stop(self):
        self.__event.set()
        return

    def run( self ):
        while not self.__event.is_set():
            currentTimeStamp = 0
            stat = os.stat( self.__masterConfig )
            if currentTimeStamp < stat.st_mtime:
                currentTimeStamp = stat.st_mtime

            for configFile in self.__optionConfig:
                stat = os.stat( configFile )
                if currentTimeStamp < stat.st_mtime:
                    currentTimeStamp = stat.st_mtime

            if self.__lastTimeStamp < currentTimeStamp:
                if self.log.hasHandlers():
                    self.log.warning( 'Reloading configuration' )

                else:
                    print( "Loading configuration" )

                self.reload()

            # Her we wait for a minute of when the event is set
            self.__event.wait( 10 )

        return

    def reload(self):
        self.__loading = True
        self.__updateIndex += 1
        self.load( self.__masterConfig )
        log_cfg = self.__configuration.get( 'logging' )
        if isinstance( log_cfg, dict ):
            logging.config.dictConfig( log_cfg )

        for configFile in self.__optionConfig:
            if os.path.exists( configFile ):
                self.load( configFile )

            else:
                raise FileNotFoundError( f"Could not load { configFile }" )

        self.__loading = False
        return

    @property
    def isLoading(self):
        return self.__loading

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

    def load(self, config_file: str):
        if self.log.hasHandlers():
            self.log.info( f"Loading configuration: {config_file}" )

        else:
            print( f"Loading configuration: {config_file}" )

        try:
            currentTimeStamp = self.__lastTimeStamp
            with open( config_file, "r" ) as stream:
                stat = os.fstat( stream.fileno() )
                if currentTimeStamp < stat.st_mtime:
                    currentTimeStamp = stat.st_mtime

                config = yaml.load(stream, Loader=yaml.Loader)
                # Copy the configuration
                for key, value in config.items():
                    if key == 'objects':
                        if key in self.__configuration:
                            # This is the list with actions
                            self.__updateObjects( value, self.__configuration[ key ] )

                        else:
                            for item in value:
                                self.__configuration.setdefault( key, [] ).append( copy.copy( item ) )

                    else:
                        self.__configuration[ key ] = value

                self.__configuration[ 'index' ]     = self.__updateIndex
                self.__configuration[ 'update_dt' ] = datetime.now()

            self.__lastTimeStamp = currentTimeStamp
            # for item in self.__configuration[ 'objects' ]:
            #     if item.get( 'index', 0 ) < self.__updateIndex:
            #         item[ 'enabled' ] = False
        except Exception:
            self.log.exception( "During loading of the configuration" )
            exit( -1 )

        return

    @property
    def Configuration( self ) -> dict:
        return self.__configuration

    def get( self, key, default_value = None ):
        return self.__configuration.get( key, default_value )
