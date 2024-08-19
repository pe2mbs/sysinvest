# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import typing as t
import traceback
import logging
from sysinvest.common.interfaces import TaskStatus
from sysinvest.server.home import blueprint
from flask import render_template, request, current_app
from flask_login import login_required
from jinja2 import TemplateNotFound
from sysinvest.server.authentication.demo import HOSTS
from sysinvest.server.api.models import Hosts, Events


logger = logging.getLogger( 'sysinvest.route' )


class HostInformation( object ):
    def __init__( self, event: Events ) -> None:
        self.href = '#'
        self.hostname = event.hostname
        self.timestamp = event.timestamp
        self.caption = event.source
        self.status = event.result
        self.info = event.message
        return

    @property
    def StatusText( self ):
        STATUSSES = [ "Collecting", "Ok", "Warning", "Failed" ]
        return STATUSSES[ self.status.value ]

    @property
    def StatusCode( self ) -> int:
        logger.info( f"StatusCode: {self.status.value}" )
        return self.status.value

    @property
    def Time( self ):
        return self.timestamp.strftime( "%Y-%m-%d %H:%M:%S" )

class HostServices( list ):
    def __init__( self ) -> None:
        super().__init__()
        self.__ok = 0
        self.__warn = 0
        self.__fail = 0
        return

    def append( self, obj ):
        if isinstance( obj, Events ):
            obj = HostInformation( obj )

        else:
            raise Exception( "Incorrect object" )

        if obj.status == TaskStatus.OK:
            self.__ok += 1
            obj.css = 'link-success'

        elif obj.status == TaskStatus.WARNING:
            self.__warn += 1
            obj.css = 'link-warning'

        elif obj.status == TaskStatus.FAILED:
            self.__fail += 1
            obj.css = 'link-danger'

        obj.info = obj.info.replace('\r','').split('\n')
        return super().append( obj )

    @property
    def ok( self ) -> int:
        return self.__ok

    @property
    def warn( self ) -> int:
        return self.__warn

    @property
    def fail( self ) -> int:
        return self.__fail

    def set( self, ok, warn, fail ):
        self.__ok = ok
        self.__warn = warn
        self.__fail = fail
        return

    @property
    def Hosts( self ) -> t.List[ str ]:
        return [ hostRecord.hostname for hostRecord in Hosts.query.filter( Hosts.active ).all() ]


def allHosts():
    allServices = HostServices()
    for hostRecord in Hosts.query.filter( Hosts.active ).all():
        for eventRecord in Events.query.filter( Events.hostname == hostRecord.hostname ):
            allServices.append( eventRecord )

    return allServices


@blueprint.route('/index')
@login_required
def index():

    try:
        allServices = allHosts()
        return render_template( 'home/index.html', segment='index.html', hosts = allServices.Hosts, allServices = allServices )
    
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        print( traceback.format_exc() )
        
    return render_template('home/page-500.html'), 500
        

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)
        HOSTS = [ hostRecord.hostname for hostRecord in Hosts.query.filter( Hosts.active ).all() ]
        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment, hosts = HOSTS, allServices = allHosts() )

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        current_app.logger.exception( f"Requesting URL: {template}" )

    return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None



@blueprint.route('/hosts/<string:host>')
@login_required
def hosts( host: str ):
    services = HostServices()
    for hostRecord in Hosts.query.filter( Hosts.hostname == host ).all():
        for eventRecord in Events.query.filter( Events.hostname == hostRecord.hostname ):
            services.append( eventRecord )

    if len( services ) == 0:
        return render_template( 'home/page-404.html' ), 404

    try:
        # Generate the detail host page
        HOSTS = [ hostRecord.hostname for hostRecord in Hosts.query.filter( Hosts.active ).all() ]
        return render_template( "home/hosts.html", segment = host, services = services, hosts = HOSTS )
    
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        current_app.logger.exception( f"Requesting URL: \hosts\{host}" )

    return render_template('home/page-500.html'), 500
