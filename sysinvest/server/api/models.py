from sysinvest.server import db
import sysinvest.common.interfaces as intf
import gzip
from sqlalchemy.types import TypeDecorator, LargeBinary
import orjson


class JSONEncodedDict( TypeDecorator ):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance( value, ( str, bytes ) ):
            value = orjson.loads( value )

        if isinstance( value, ( list, dict ) ):
            value = gzip.compress( orjson.dumps( value ) )

        return value

    def process_result_value(self, value, dialect):
        if isinstance( value, bytes ):
            if value.startswith(b'{') and value.endswith(b'}'):
                value = orjson.loads( value )

            elif value.startswith( b'\x1f\x8b\x08\x00' ):
                value = orjson.loads( gzip.decompress( value ) )

        return value





class Hosts( db.Model ):
    __tablename__   = 'Hosts'
    id              = db.Column( db.Integer, primary_key = True )
    active          = db.Column( db.Boolean, default = False )
    hostname        = db.Column( db.String( 64 ), unique = True )
    location        = db.Column( db.String( 256 ) )
    token           = db.Column( db.LargeBinary )


class Events( db.Model ):
    __tablename__   = 'Events'
    id              = db.Column( db.Integer, primary_key = True )
    timestamp       = db.Column( db.DateTime( timezone=True ) )
    source          = db.Column( db.String(64) )
    hostname        = db.Column( db.String(64) )
    result          = db.Column( db.Enum( intf.TaskStatus ) )
    message         = db.Column( db.Text )
    class_name      = db.Column( db.String(64) )
    details         = db.Column( JSONEncodedDict )
    version         = db.Column( db.String(32) )
    release         = db.Column( db.String(32) )
