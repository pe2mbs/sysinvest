import typing as t
import logging
from datetime import datetime
import sysinvest.version as version
import requests
import pytz
import orjson
from sysinvest.common.interfaces import TaskStatus, AgentRequest, DetailBaseData


logger = logging.getLogger('sysinvest.simpel')


class SingleStatusApi( object ):
    def __init__( self, name: str, hostname: str, remote_url: str, timezone: str = 'Europe/Amsterdam'  ):
        self.__hostname = hostname
        self.__url      = remote_url
        self.__ts       = pytz.timezone( timezone )
        self.__name     = name
        return

    def send( self, status: TaskStatus, message: str, server_data: t.Optional[ DetailBaseData ] = None ):
        if server_data is None:
            class_name = None

        elif isinstance( server_data, list ) and len( server_data ) > 0:
            class_name = server_data[ 0 ].__class__.__name__

        else:
            class_name = server_data.__class__.__name__

        req = AgentRequest( timestamp = datetime.now( self.__ts ),
                            source = self.__name,
                            result = status,
                            details = server_data,
                            message = message,
                            class_name = class_name,
                            hostname = self.__hostname,
                            version = version.version,
                            release = version.date )
        logger.info( f"Sending to {self.__url}" )
        r = requests.post( self.__url, data = orjson.dumps( req.dict() ), headers = { "Content-Type": "application/json" } )
        logger.info( f"STATUS {r.status_code} - {r.content}" )
        return ( r.status_code == 200 and r.content == b'Ok' )
