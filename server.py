from flask import Flask
import orjson
from flask_pydantic import validate
import sysinvest.common.interfaces as intf


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/agent", methods = [ 'POST' ] )
@validate()
def agent( body: intf.AgentRequest ):
    # print( body )
    try:
        _class = getattr( intf, body.class_name )

    except:
        _class = None

    print( "-" * 20 )
    print( f"Task:      { body.source } from host {body.hostname}")
    print( f"Agent:     { body.version } - { body.release }")
    print( f"Timestamp: { body.timestamp }" )
    print( f"Message:   { body.message }" )
    print( f"Result:    { body.result }" )
    print( f"Class:     { _class }" )
    if _class is not None:
        print( f"Details:" )
        if isinstance( body.details, list ):
            for item in body.details:
                _class( **item ).pprint()

        else:
            _class( **body.details ).pprint()

    elif isinstance( body.details, dict ):
        print( f"Details:   { orjson.dumps( body.details, option = orjson.OPT_INDENT_2 ) }" )

    print( "-" * 20 )
    return "OK"