from mako.template import Template
from datetime import datetime, timedelta, date, time
import pymysql
import pymysql.cursors
from pymysql.err import MySQLError
from sysinvest.common.plugin import PluginResult, ReportPlugin
import sysinvest.common.api as API


class ReportMySql( ReportPlugin ):
    def __init__( self, config: dict ):
        super().__init__( 'database', config )
        self.__collected = []
        self.log.info( f"ReportMySql initialized: {self.Config}" )
        return

    def notify(self, result: PluginResult):
        if not result.Result or result.Plugin.Priority:
            self.__collected.append( result )

        return

    def publish(self):
        if len( self.__collected ) == 0:
            # Nothing to do
            return

        message = '\n\n'.join( [ result.buildMessage().replace('\\', '\\\\') for result in self.__collected ] )
        schema = self.Config.get('schema')
        with pymysql.connect( host = self.Config.get( 'hostname', 'localhost' ),
                              port = int( self.Config.get( 'hostport', 3306 ) ),
                              user = self.Config.get( 'username' ),
                              password = self.Config.get( 'password' ),
                              database = schema,
                              cursorclass = pymysql.cursors.DictCursor ) as connection:
            with connection.cursor() as cursor:
                insert = self.Config.get( 'insert' )

                sql = Template( insert ).render( datetime = datetime, message = message, schema = schema )
                if not sql.endswith(';'):
                    sql += ";"

                self.log.info( f"SQL statement: {sql}" )
                cursor.execute( "BEGIN WORK;" )
                cursor.execute( sql )
                cursor.execute( "COMMIT WORK;" )

        self.__collected = []
        return

