import urllib.parse


class SqlBaseClass( object ):
    def __init__( self, config: dict ):
        self._session = None
        self._config = config
        self._url = urllib.parse.urlparse( self._config.get( 'url' ) )
        self._resultType = config.get( 'type', 'rows' )
        return

    def __enter__(self):
        return self._session

    def __exit__(self, *exc_info):
        del exc_info
        self._session.close()
        return