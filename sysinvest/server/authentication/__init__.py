# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os.path
from flask import Blueprint

blueprint = Blueprint(
    'authentication_blueprint',
    __name__,
    url_prefix='',
    template_folder=os.path.join( os.path.dirname(__file__),  '..', 'templates' )
)
