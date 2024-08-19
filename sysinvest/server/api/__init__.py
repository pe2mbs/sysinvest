import os.path
from flask import Blueprint

blueprint = Blueprint(
    'api_blueprint',
    __name__,
    url_prefix='',
    template_folder=os.path.join( os.path.dirname(__file__),  '..', 'templates' )
)