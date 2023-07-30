from typing import List
from sysinvest.common.config.configuration import ConfigLoader
from datetime import datetime
import yaml
import os
import copy
import logging.config


class ConfigLoaderYaml( ConfigLoader ):
    def __init__( self, master_config: str, *option_config, **kwargs ):
        self.__masterConfig: str        = master_config
        self.__optionConfig: List[str]  = list( option_config )
        super().__init__()
        return

    def checkForReload( self ) -> bool:
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
                return True

        return False

    def reload( self ):
        self.__loadingEvent.set()
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

        self.__loadingEvent.clear()
        return

    def load(self, config_file: str):
        if self.log.hasHandlers():
            self.log.info( f"Loading configuration: {config_file}" )

        else:
            print( f"Loading configuration: {config_file}" )

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
        for item in self.__configuration[ 'objects' ]:
            if item.get( 'index', 0 ) < self.__updateIndex:
                item[ 'enabled' ] = False

        return
