import os
import sys
import yaml
import getopt
import logging
from datetime import datetime
from flask import Flask
from mako.template import Template
from flask_sysinvest_clt import SysInvestExtension


app = Flask( __name__ )

@app.route("/")
def index():
    return "Hello world this is the flask_sysinvest_srv"

def banner():
    print()
    return


def usage():
    print()
    return


def main():
    banner()
    logging.basicConfig( stream = sys.stdout, format = '%(asctime)s %(levelname)s %(message)s', level = logging.DEBUG )
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])

    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    config = {}
    devMode = False
    for o, a in opts:
        if o == "-v":
            logging.getLogger().setLevel( logging.DEBUG )

        elif o in ("-h", "--help"):
            usage()
            sys.exit()

        elif o in ("-d", "--dev"):
            devMode= True

        elif o in ( "-c", "--config" ):
            with open( a, 'r' ) as stream:
                config.update( yaml.load( stream, Loader = yaml.Loader ) )

        else:
            assert False, "unhandled option"

    staticFolder = config.get( 'static-folder', os.path.join( os.path.dirname( __file__ ), 'static' ) )
    app.config[ 'SYSINVEST' ] = {
        'static_folder': staticFolder,
        'tasks': config.get( 'monitor-config', ( '/home/mbertens/src/python/monitor/config.conf', ) )
    }
    sysinvestCls = SysInvestExtension( app )
    if devMode:
        from werkzeug.serving import run_simple
        # Call werkzeug direcly
        run_simple( hostname = config.get( 'hostname', 'localhost' ),
                    port = config.get( 'hostport', 5000 ),
                    application = app,
                    use_reloader = True,
                    use_debugger = True,
                    static_files = { '/static': staticFolder }
        )
        # Call via Flask
        # app.run( host = config.get( 'hostname', 'localhost' ),
        #          port = config.get( 'hostport', 5000 ),
        #          static_files = { '/static': staticFolder } )
    else:
        from waitress import serve
        # Run it through the production server
        serve( app,
               host = config.get( 'hostname', 'localhost' ),
               port = config.get( 'hostport', 5000 ) )



if __name__ == '__main__':
    main()