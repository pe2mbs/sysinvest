import orjson
from sysinvest.server.api import blueprint
import sysinvest.common.interfaces as intf
from sysinvest.server.api.models import Hosts, Events
from sqlalchemy.exc import NoResultFound
from sysinvest.server import db
from flask import current_app, request
from flask_pydantic import validate

@blueprint.route( '/api/agent', methods = [ 'POST', 'GET' ] )
@validate()
def agent( body: intf.AgentRequest ):
    print( f'agent: {body}')
    host = Hosts.query.filter( Hosts.hostname == body.hostname ).one_or_none()
    if host is None:
        current_app.logger.error( f"{body.hostname} is not a registered host for sysInvest"  )
        return "NOK"

    else:
        auth = request.headers.get( 'AUTH' )
        host: Hosts
        if host.token != auth:
            current_app.logger.warning( f"{body.hostname} has not token" )

    try:
        _class = getattr( intf, body.class_name )

    except:
        _class = None

    try:
        record = Events.query.filter( Events.hostname == body.hostname ).filter( Events.source == body.source ).one()
        record.timestamp = body.timestamp
        record.result = body.result
        record.message = body.message
        record.class_name = body.class_name
        record.details = body.details
        record.version = body.version
        record.release = body.release

    except NoResultFound:
        try:
            record = Events( timestamp = body.timestamp,
                     source = body.source,
                     hostname = body.hostname,
                     result = body.result,
                     message = body.message,
                     class_name = body.class_name,
                     details = body.details,
                     version = body.version,
                     release = body.release )
            db.session.add( record )

        except Exception:
            current_app.logger.exception( "During Monitor insert" )

    except Exception:
        current_app.logger.exception( "During Monitor update" )

    db.session.commit()
    current_app.logger.info( "-" * 20 )
    current_app.logger.info( f"Task:      { body.source } from host {body.hostname}")
    current_app.logger.info( f"Agent:     { body.version } - { body.release }")
    current_app.logger.info( f"Timestamp: { body.timestamp }" )
    current_app.logger.info( f"Message:   { body.message }" )
    current_app.logger.info( f"Result:    { body.result }" )
    current_app.logger.info( f"Class:     { _class }" )
    if _class is not None:
        print( f"Details:" )
        if isinstance( body.details, list ):
            for item in body.details:
                _class( **item ).log( current_app.logger.info )

        else:
            _class( **body.details ).log( current_app.logger.info )

    elif isinstance( body.details, dict ):
        current_app.logger.info( f"Details:   { orjson.dumps( body.details, option = orjson.OPT_INDENT_2 ) }" )

    current_app.logger.info( "-" * 20 )
    return "OK"

