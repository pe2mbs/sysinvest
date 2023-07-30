from sysinvest.common.config.configuration import ConfigLoader
from sqlalchemy import create_engine,Column,String,Integer,DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from json import dumps as json_dump_str

base = declarative_base()


class DbVersion( base ):
    __tablename__       = 'version'
    v_id                = Column( Integer, primary_key=True, autoincrement = True )
    v_version           = Column( Integer )
    v_datetime          = Column( DateTime )


class DbConfig( base ):
    __tablename__       = 'config'
    c_id                = Column( Integer, primary_key=True, autoincrement = True )
    c_logging_config    = Column( String )


class DbRules( base ):
    __tablename__       = 'rules'
    r_id                = Column( Integer, primary_key=True, autoincrement = True )
    r_enabled           = Column( Boolean )
    r_name              = Column( String( 80 ) )
    r_cron              = Column( String( 10 ) )
    r_priority          = Column( Boolean, default = False )
    r_group             = Column( String( 20 ), default = "" )
    r_hits              = Column( Integer, default = 1 )
    r_ticket            = Column( Boolean, default = True )
    r_module            = Column( String( 80 ) )
    r_template          = Column( Text )

    attributes          = relationship( 'DbRuleAttributes', back_populates='rule' )

class DbRuleAttributes( base ):
    __tablename__       = 'rule_attributes'
    a_id                = Column( Integer, primary_key=True, autoincrement = True )
    a_r_id              = Column( Integer, ForeignKey( 'rules.r_id' ) )
    a_index             = Column( Integer )
    a_name              = Column( String( 80 ) )
    a_type_value        = Column( String( 10 ) )
    a_value             = Column( Text )

    rule                = relationship( 'DbRules', back_populates = 'attributes' )

class DbNotify( base ):
    __tablename__       = 'notify'
    n_id                = Column( Integer, primary_key=True, autoincrement = True )
    n_name              = Column( String( 80 ) )
    n_enabled           = Column( Boolean )
    a_module            = Column( String( 80 ) )

    attributes          = relationship( 'DbNotifyAttributes', back_populates='parent' )

class DbNotifyAttributes( base ):
    __tablename__       = 'notify_attributes'
    a_id                = Column( Integer, primary_key=True, autoincrement = True )
    a_n_id              = Column( Integer, ForeignKey( 'notify.n_id' ) )
    a_index             = Column( Integer, default = -1 )
    a_name              = Column( String( 80 ) )
    a_type_value        = Column( String( 10 ) )
    a_value             = Column( Text )

    notify              = relationship( 'DbNotify', back_populates = 'attributes' )


class ConfigLoaderDatabase( ConfigLoader ):
    """
        Datebase
            version
                V_id                int         autonumber
                v_version           int
                v_datetime          datetime

            config:
                c_id                int         autonumber
                c_logging_config    str         filename (.yaml, .json ) | text in YAML or JSON

            rules
                r_id                int         autonumber
                r_enabled           bool
                r_cron              str
                r_priority          bool
                r_group             str
                r_hits              int
                r_ticket            bool
                r_module            str
                r_template          str

            attributes
                a_id                int         autonumber
                a_r_id              int         foreign key
                a_index             int         -1, 0...
                a_name              str
                a_type_value        str         str,int,float
                a_value             str

            notify:
                n_id                int         autonumber
                n_name              str
                n_enabled           bool
                a_module            str

            parameters
                p_id                int         autonumber
                p_n_id              int         foreign key
                p_name              str
                p_type_value        str         str,int,float
                p_value             str

    """
    def __init__( self ):
        super().__init__()
        db_url = { 'drivername': 'sqlite', 'database': './test.db' }
        self.__engine = create_engine( URL( **db_url ) )
        base.metadata.create_all( bind = self.__engine )
        self.__session = sessionmaker( bind = self.__engine )()
        return

    @property
    def Session( self ):
        return self.__session

    def checkForReload( self ) -> bool:
        return False

    def reload( self ):
        return


if __name__ == '__main__':
    db = ConfigLoaderDatabase()
    session = scoped_session( db.Session )
    try:
        session.add( DbVersion( v_version = 1, v_datetime = datetime.utcnow() ) )
        session.add( DbConfig( c_logging_config = json_dump_str( {
            "version": 1,
            "formatters": {
                "short": {
                    "format": '%(message)s'
                },
                "brief": {
                    "format": '%(asctime)s %(levelname)-8s "%(name)-25s" %(message)s',
                    "datefmt": '%Y-%m-%d %H:%M:%S'
                },
                "precise": {
                    "format": '%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
                    "datefmt": '%Y-%m-%d %H:%M:%S'
                }
            },
            "handlers": {
                "console":{
                    "class": "logging.StreamHandler",
                    "formatter": "brief",
                    "level": "DEBUG",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "precise",
                    "filename": "logconfig.log",
                    "maxBytes": 10240000,
                    "backupCount": 3
                }
            },
            "loggers": {
                "monitor": {
                    "level": "DEBUG",
                    "handlers": [ "console", "file" ]
                },
                "result": {
                    "level": "DEBUG",
                    "handlers": [ "console", "file" ]
                },
                "collector": {
                    "level": "DEBUG",
                    "handlers": [ "console", "file" ]
                },
                "plugin":{
                    "level": "DEBUG",
                    "handlers": [ "console", "file" ]
                },
                "tasks": {
                    "level": "DEBUG",
                    "handlers": [ "console", "file" ]
                },
                "html":{
                    "level": "DEBUG",
                    "handlers": [ "console", "file" ]
                }
            },
            "root": {
                "level": "DEBUG",
                "handlers": [ "console", "file" ]
            } } ) ) )

        jira = DbNotify(
            n_name              = "jira",
            n_enabled           = False,
            a_module            = "report.jira"
        )
        session.add( jira )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id,
                                         a_name = 'host', a_type_value = "str", a_value = "jira.pe2mbs.nl"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id,
                                         a_name = 'username', a_type_value = "str", a_value = "monitor"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id,
                                         a_name = 'password', a_type_value = "str", a_value = "verysecret"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id,
                                         a_name = 'project', a_type_value = "str", a_value = "Monitor Infra"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id,
                                         a_name = 'issue', a_type_value = "str", a_value = "Task"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id, index = 0,
                                         a_name = 'assignee', a_type_value = "str", a_value = "1st line support"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id, index = 1,
                                         a_name = 'assignee', a_type_value = "str", a_value = "2nd line support"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = jira.n_id,
                                         a_name = 'description', a_type_value = "str", a_value = "${ message }"
                                         ) )

        html = DbNotify(
            n_name              = "html",
            n_enabled           = True,
            a_module            = "report.html"
        )
        session.add( html )
        session.add( DbNotifyAttributes( a_n_id = html.n_id,
                                         a_name = 'template', a_type_value = "str", a_value = "./template_index.html"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = html.n_id,
                                         a_name = 'location', a_type_value = "str", a_value = "/var/www/sysinvest/index.html"
                                         ) )
        session.add( DbNotifyAttributes( a_n_id = html.n_id,
                                         a_name = 'interval', a_type_value = "int", a_value = "60"
                                         ) )

        session.add( DbRules(
            r_enabled           = True,
            r_name              = "I am alive",
            r_cron              = "0 0 * * *",
            r_module            = "iamalive",
            r_template          = "SysInvest infrastructure monitor daemon is alive, running since ${since}\n" +
                                  "Uptime ${uptime} with no. ${passes} passes, checking ${tasks} tasks",
        ) )
        serverloads = DbRules(
            r_enabled           = True,
            r_name              = "Check server loads",
            r_cron              = "*/1 * * * *",
            r_module            = "serverloads",
            r_template          = "",
        )
        session.add( serverloads )
        session.add( DbRuleAttributes( a_r_id = serverloads.r_id,
                                       a_name = 'memory',
                                       a_type_value = 'int',
                                       a_value = '80' ) )



        session.commit()

    except SQLAlchemyError as e:
        session.rollback()

    finally:
        session.close()





