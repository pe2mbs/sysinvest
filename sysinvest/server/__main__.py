# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import typing as t
import os
import click
import waitress
from flask.cli import with_appcontext, FlaskGroup, main as flask_main
from flask_migrate import Migrate
from flask_minify import Minify
from paste.translogger import TransLogger
from sysinvest.server.api.models import Hosts
from sysinvest.server import create_app, db
from sysinvest.server.authentication.models import Users

app = create_app( os.getcwd() )
Migrate( app, db )


if not app.config[ 'DEBUG' ]:
    Minify( app = app, html = True, js = False, cssless = False )

if app.config[ 'DEBUG' ]:
    app.logger.info( 'DEBUG            = ' + str( app.config[ 'DEBUG' ] ) )
    app.logger.info( 'FLASK_ENV        = ' + os.getenv( 'FLASK_ENV', '' ) )
    app.logger.info( 'Page Compression = ' + 'FALSE' if app.config[ 'DEBUG' ] else 'TRUE' )
    app.logger.info( 'DBMS             = ' + app.config[ 'SQLALCHEMY_DATABASE_URI' ] )
    app.logger.info( 'ASSETS_ROOT      = ' + app.config[ 'ASSETS_ROOT' ] )


@app.cli.group( 'dba', cls = FlaskGroup )
def dba_cli():
    pass

@dba_cli.group( 'add', cls = FlaskGroup )
def dba_add_cli():
    pass

@dba_add_cli.command("server")
@click.argument( "fqdn" )
@click.argument( "location" )
@click.argument( "token", required = False )
@with_appcontext
def create_user( fqdn, location, token: t.Optional[ str ] = None ):
    rec = Hosts( hostname = fqdn, location = location, token = token, active = True )
    db.session.add( rec )
    db.session.commit()
    return


@dba_add_cli.command("user")
@click.argument( "username" )
@click.argument( "email" )
@click.argument( "password" )
@with_appcontext
def create_user( username, email, password ):
    rec = Users( username = username, email = email, password = password, active = True )
    db.session.add( rec )
    db.session.commit()
    return


@app.cli.group( 'serve', cls = FlaskGroup )
def serve_cli():
    pass


@serve_cli.command("production")
def serve_production():
    app.logger.warning("Starting the production server")
    os.environ.pop( "FLASK_RUN_FROM_CLI" )
    host = app.config.get( 'HOST', '0.0.0.0' )
    port = app.config.get( 'PORT', 5001 )
    waitress.serve( TransLogger( app, setup_console_handler = False ), listen = f'{host}:{port}' )
    app.logger.warning( "Shutting down production server" )
    return

@serve_cli.command( "dev" )
def serve_development():
    os.environ.pop( "FLASK_RUN_FROM_CLI" )
    app.logger.warning("Starting the develpment server")
    host = app.config.get( 'HOST', '0.0.0.0' )
    port = app.config.get( 'PORT', 5001 )
    app.run( host, port, debug = True )
    app.logger.warning( "Shutting down the develpment server" )


def main():
    if 'FLASK_APP' not in os.environ:
        os.environ[ 'FLASK_APP' ] = 'sysinvest.server.__main__.py'

    flask_main()


if __name__ == "__main__":
    if 'FLASK_APP' not in os.environ:
        os.environ[ 'FLASK_APP' ] = 'sysinvest.server.__main__.py'

    flask_main()

