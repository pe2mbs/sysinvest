from datetime import datetime
from mako.template import Template
from flask import Blueprint
from sysinvest.execute import execute
import sysinvest.common.api as API
from sysinvest.common.configuration import ConfigLoader, InvalidConfig
from sysinvest.common.plugin.monitor import MonitorPlugin


class SysInvestExtension:
    def __init__( self, app = None,  ):
        self.simple_page = Blueprint( 'sysinvest', __name__ )
        self.simple_page.add_url_rule( '/sysinvest', view_func = self.monitorPage, methods = [ 'GET' ] )
        self.simple_page.add_url_rule( '/sysinvest_info', view_func = self.showInfo, methods = [ 'GET' ] )

        if app is not None:
            self.init_app( app )
            app.register_blueprint( self.simple_page )

        return

    def init_app( self, app ):
        config = app.config[ 'SYSINVEST' ]
        if isinstance( config, dict ):
            tasks = config.get( 'tasks' )
            self.simple_page.static_folder = config.get( 'static_folder', '.' )

        else:
            tasks = config

        if isinstance( tasks, str ):
            # Do the configuration loading
            cfgClass = ConfigLoader( tasks )

        elif isinstance( tasks, (list,tuple) ):
            cfgClass = ConfigLoader( *tasks )

        elif isinstance( tasks, ConfigLoader ):
            cfgClass = tasks

        else:
            raise InvalidConfig()

        cfgClass.whileIsLoading()
        # Run this as a thread
        execute( cfgClass, True )
        return

    def showInfo( self ):
        return "SysInvest - main page"


    COLORS = {
        'OK': 'green',
        'FAILED': 'red',
        'WARNING': 'yellow'
    }

    def monitorPage( self ):
        tasks = []
        for task in API.Monitor:
            task: MonitorPlugin
            tasks.append( {
                'name': task.Name,
                'enabled': task.Enabled,
                'status': task.Status,
                'message': task.Message,
                'color': self.COLORS[ task.Status ]
            })


        with open( 'static/templates/index.mako', 'r' ) as stream:
            pageTemplate = stream.read()

        return Template( pageTemplate ).render( tasks = tasks,
                                                interval = 60,
                                                computername = 'TEST',
                                                lastTime = datetime.now(),
                                                configIndex = 1,
                                                configDateTime = datetime.now(),
                                                )
