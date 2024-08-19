import typing as t
import logging
from datetime import datetime
import sysinvest.version as version
import requests
import pytz
import orjson
from sysinvest.common.interfaces import TaskStatus, AgentRequest, DetailBaseData





class StatusManager():
    def __init__( self, hostname: str, remote_url: str, timezone: str = 'Europe/Amsterdam' ):
        self.__hostname = hostname
        self.__url      = remote_url
        self.__ts       = pytz.timezone( timezone )
        return

    def send( self ):
        return
