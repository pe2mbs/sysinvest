import pymysql
import pymysql.cursors
from pymysql.err import MySQLError
from sysinvest.agent.plugins.sql.base import SqlBaseClass


SqlError = MySQLError


class SqlClass( SqlBaseClass ):
    def connect( self ):
        database = self._url.path[1:]
        self._session = pymysql.connect( host = self._url.hostname,
                                         port = self._url.port,
                                         user = self._url.username,
                                         password = self._url.password,
                                         database = database,
                                         cursorclass = pymysql.cursors.DictCursor )
        return self._session





