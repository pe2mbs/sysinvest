


class ReportPlugin( object ):
    def __init__( self, name: str, config: dict ):
        self.__name = name
        self.__cfg = config.get( name, {} )
        return

    @property
    def Name( self ):
        return self.__name

    @property
    def Config( self ):
        return self.__cfg

    def notify( self, result: 'PluginResult' ):
        raise NotImplemented()

    def publish( self ):
        raise NotImplemented()


