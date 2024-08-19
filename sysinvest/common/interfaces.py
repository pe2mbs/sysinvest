import enum
import typing as t

import orjson
from pydantic import BaseModel
from datetime import datetime

class MyBaseModel( BaseModel ):
    def pprint( self ):
        print( orjson.dumps( BaseModel.dict( self ), option = orjson.OPT_INDENT_2 ).decode('utf-8') )
        return

    def log( self, caller ):
        caller( orjson.dumps( BaseModel.dict( self ), option = orjson.OPT_INDENT_2 ).decode( 'utf-8' ) )
        return;

class TaskStatus( enum.Enum ):
    COLLECTING = 0
    OK = 1
    WARNING = 2
    FAILED = 3


class AgentRequest( MyBaseModel ):
    timestamp:      datetime
    source:         str
    hostname:       str
    result:         TaskStatus
    message:        str
    class_name:     t.Optional[ str ]
    details:        t.Optional[ t.Any ]
    version:        t.Optional[ str ]
    release:        t.Optional[ str ]

class DetailBaseData( MyBaseModel ):
    since:          datetime
    lasttime:       datetime
    tasks:          int
    hits:           int = 0



class ProcessData( DetailBaseData ):
    percent:        float = 0.0
    cpu:            int = 0
    affinity:       t.List[ int ] = [ 0 ]
    user:           float = 0.0
    system:         float = 0.0
    name:           str = ''
    username:       str = ''
    status:         str = 'initializing'
    created:        datetime = 0.0
    ctx_switches:   t.List[ int ] = [ 0 ]
    no_threads:     int = 0
    read_cnt:       int = 0
    write_cnt:      int = 0
    read_bytes:     int = 0
    write_bytes:    int = 0
    rss:            int = 0
    vms:            int = 0
    pfaults:        int = 0
    pid:            int = 0


class ExceptionData( MyBaseModel ):
    exception:      str
    stacktrace:     t.List[ str ]


class CpuLoadData( MyBaseModel ):
    core:           int
    minute_1_load:  float
    minute_5_load:  float
    minute_15_load: float


class OverallCpuLoadData( MyBaseModel ):
    minute_1_load:  float
    minute_5_load:  float
    minute_15_load: float
    cores:          t.List[ CpuLoadData ]
    percent:        float

class MemoryLoadData( MyBaseModel ):
    total:          int
    available:      int
    percent:        float


class ServerLoadsData( DetailBaseData ):
    cpu:            bool = False
    mem:            bool = False
    messages:       t.List[ str ]
    cpuLoad:        OverallCpuLoadData
    memload:        MemoryLoadData


class NetworkInterface( BaseModel ):
    interface:  str
    address:    str
    hostname:   str
    media:      str
    threshold:  int = 0


class NetworkData( MyBaseModel ):
    Interface:              str
    ReceiveBytes:           int
    TransmitBytes:          int
    ReceiveSpeed:           int
    TransmitSpeed:          int
    AverageReceiveSpeed:    float
    AverageTransmitSpeed:   float

    def setAverage( self, rx, tx ):
        self.AverageReceiveSpeed = rx
        self.AverageTransmitSpeed = tx
        return


class FileExists( MyBaseModel ):
    filename:   str
    exists:     bool
    expired:    bool
    size_valid: bool
    mode:       t.Optional[ str ] = None
    ino:        t.Optional[ int ] = None
    dev:        t.Optional[ int ] = None
    nlink:      t.Optional[ int ] = None
    uid:        t.Optional[ int ] = None
    gid:        t.Optional[ int ] = None
    size:       t.Optional[ int ] = None
    atime:      t.Optional[ float ] = None
    mtime:      t.Optional[ float ] = None
    ctime:      t.Optional[ float ] = None


class HtmlElement( MyBaseModel ):
    label:  str
    value:  str
    valid:  bool


class HttpResponse( MyBaseModel ):
    status_code:    int
    content:        t.Optional[ str ] = None
    elapsed:        t.Optional[ int ] = None
    headers:        t.Optional[ dict ] = None
    encoding:       t.Optional[ str ] = None
    elements:       t.Optional[ t.List[ HtmlElement ] ] = None

class RedisResponse( MyBaseModel ):
    status_code:    int



class SQLRow( MyBaseModel ):
    field:          str
    value:          t.Any


class SqlResult( MyBaseModel ):
    recordcount:    int
    query:          t.Optional[ str ] = None
    expected:       t.Optional[ t.Union[ SQLRow, t.Any ] ] = None
    retrieved:      t.Optional[ t.Union[ SQLRow, t.Any ] ] = None


class EnvironmentVars( MyBaseModel ):
    name:           str
    value:          str


class EnvironmentData( MyBaseModel ):
    machine:        str
    platform:       str
    processor:      str
    version:        str
    uname:          str
    environment:    t.Optional[ t.List[ EnvironmentVars ] ] = None


class SensorData( MyBaseModel ):
    package:        str
    sensor:         str
    input:          float
    crit:           float
    max:            t.Optional[ float ] = None
    crit_alarm:     t.Optional[ float ] = None


class SensorsData( MyBaseModel ):
    features:       t.List[ SensorData ]
