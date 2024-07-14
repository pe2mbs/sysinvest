from sysinvest.agent.plugins.sql.base import SqlBaseClass
import sqlite3


SqlError    = sqlite3.DatabaseError


class SqliteRow( sqlite3.Row ):
    def dict( self ):
        result = {}
        for key in self.keys():
            result[ key ] = self[ key ]

        return result


class SqliteCursor( sqlite3.Cursor ):
    def __init__( self, connection ):
        super().__init__( connection )
        return

    def __enter__( self) :
        return self

    def __exit__( self, *exc_info ):
        del exc_info
        self.close()
        return

    def fetchall( self ):
        result = []
        for row in super().fetchall():
            result.append( row.dict() )

        return result

    def fetchone( self ):
        result = super().fetchone()
        if result is not None:
            result = result.dict()

        return result


class SqliteConnection( sqlite3.Connection ):
    def __init__( self, path: str ):
        super().__init__( path )
        self.row_factory = SqliteRow
        return

    def cursor( self, cursorClass = None ):
        return super().cursor( SqliteCursor )


class SqlClass( SqlBaseClass ):
    def connect( self ):
        self._session = SqliteConnection( self._url.path )
        return self._session
