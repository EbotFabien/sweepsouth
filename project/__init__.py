import os
from flask import Flask, Response, send_file, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
from project.Config import config 
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.http import HTTP_STATUS_CODES
import werkzeug
from werkzeug.utils import redirect

bcrypt = Bcrypt()
mail = Mail()
db = SQLAlchemy()
basedir= os.path.abspath(os.path.dirname(__file__))
cache = Cache(config={'CACHE_TYPE': 'simple'})
limiter = Limiter(key_func=get_remote_address)

SERVER_NAME = 'Google Web Server v0.1.0'

class localFlask(Flask):
    def process_response(self, response):
        #Every response will be processed here first
        response.headers['server'] = SERVER_NAME
        super(localFlask, self).process_response(response)
        return(response)

def create_app(configname):
    app = localFlask(__name__)
    app.config.from_object(config[configname])

    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    

    from project.api import models
    from .api import api  as api_blueprint
    

    app.register_blueprint(api_blueprint, url_prefix='/api')             
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/')
    def index():
        return "Hello from Odaaay-app"

    @app.route('/file/<name>')
    def filename(name):
        return send_file('./static/files/'+str(name), attachment_filename=str(name))

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return 'bad request!', 400

    @app.errorhandler(werkzeug.exceptions.NotFound)
    def handle_bad_request(e):
        return 'Not Found!', 404
        
    @app.errorhandler(werkzeug.exceptions.InternalServerError)
    def handle_bad_request(e):
        return 'Internal server error', 500

    return app
