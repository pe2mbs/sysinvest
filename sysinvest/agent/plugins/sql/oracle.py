import oracledb
from sysinvest.agent.plugins.sql.base import SqlBaseClass


SqlError = oracledb.Error

"""
    TODO: Testing
"""
class SqlClass( SqlBaseClass ):
    def connect( self ):
        self._session = oracledb.connect( host = self._url.hostname,
                                          port = self._url.port,
                                          user = self._url.username,
                                          password = self._url.password,
                                          database = self._url.path )
        return self._session