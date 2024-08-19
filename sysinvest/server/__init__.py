# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os.path
import logging.config
import yaml
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home', 'api'):
        module = import_module('sysinvest.server.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    @app.before_request
    def initialize_database():
        app.before_request_funcs[ None ].remove( initialize_database )
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def yaml_loader( filename ):
    return yaml.load( filename, Loader = yaml.Loader )


def create_app( instance_path ):
    app = Flask(__name__, root_path = instance_path, static_folder = os.path.join( os.path.dirname( __file__ ), 'static' ) )
    # app.config.from_object( config )
    app.config.from_file( 'config.yaml', load = yaml_loader )
    logData = app.config.get( 'LOGGING' )
    if isinstance( logData, dict ):
        logging.config.dictConfig( logData )

    register_extensions( app )
    register_blueprints( app )
    configure_database( app )
    return app
