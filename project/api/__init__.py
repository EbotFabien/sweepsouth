from flask import Blueprint, url_for
from flask_restplus import Api, Resource, fields, reqparse, marshal
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
import requests as rqs
#from tqdm import tqdm
from flask import current_app as app
from datetime import datetime, timedelta
from project import db, limiter, cache,bcrypt
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import werkzeug
import json, shortuuid
import uuid
import jwt, uuid, os
from flask import current_app as app
from sqlalchemy import func,or_,and_
import re
from .v1 import booking,client,comment, extra, Service, worker,location
from project.api.models import  Extras,Booking,Client,Comment,Services,Worker,Administrators


# API security
authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}


# The token decorator to protect my routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'API-KEY' in request.headers:
            token = request.headers['API-KEY']
            try:
                data = jwt.decode(token, app.config.get('SECRET_KEY'))
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated
v=1
if v==1:
    @property
    def specs_url(self):
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')
    Api.specs_url = specs_url

api = Blueprint('api', __name__, template_folder = '../templates')
apisec = Api( app=api, doc='/docs', version='1.9.0', title='Sweep south demo.', \
    description='This documentation contains all routes to access the Sweep south API. \npip install googletransSome routes require authorization and can only be gotten \
    from the sweepsouth company', license='../LICENSE', license_url='www.sweep.com', contact='touchone0001@gmail.com', authorizations=authorizations)
CORS(api, resources={r"/api/*": {"origins": "*"}})

from . import schema

apisec.add_namespace(booking)
apisec.add_namespace(client)
apisec.add_namespace(extra)
apisec.add_namespace(Service)
apisec.add_namespace(worker)
apisec.add_namespace(comment)
apisec.add_namespace(location)


login = apisec.namespace('/api/auth', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ', \
    path='/v1/')

signup = apisec.namespace('/api/auth', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ', \
    path='/v1/')

@login.doc(
    params={
        'email': 'Type of service',
        'password': 'Type of service',
    },

    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        405:'method not allowed',
        500: 'internal server error, please contact admin and report issue'
    })
@login.route('/test')
class Test(Resource):
    def post(self):
            print(request.form.get('email',None))
            email = request.args.get('email',None)
            password = request.args.get('password',None)
            if email is not None:
                return {
                        'status': email,
                        'res': 'Working',
                        }, 200
            else:
                return {
                        'status':0,
                        'res': 'not Working',
                        }, 405
   
@login.doc(
    params={},

    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })
@login.route('/auth/login')
class Login(Resource):
    #@login.expect(schema.full_login)
    def post(self):
        app.logger.info('User login with user_name')
        req_data = request.form
        if req_data:
            login_type='admin'#req_data['login_type']
            email=req_data.get('email',None) 
            password=req_data.get('password',None)
            if login_type == 'client' :
                user = Client.query.filter_by(email=email).first()
                if user:
                    if user.verify_password(password):
                        token = jwt.encode({
                            'user': user.email,
                            'uuid': user.uuid,
                            'iat': datetime.utcnow()
                        },
                        app.config.get('SECRET_KEY'),
                        algorithm='HS256')
                        string_token = str(token)
                        return {
                            'status': 1,
                            'res': 'success',
                            'token': string_token
                        }, 200
                else:
                    return {
                            'status': 0,
                            'res': "Client doesn't exist",
                        }, 401
            if login_type == 'worker' :
                user = Worker.query.filter_by(email=email).first()
                if user:
                    if user.verify_password(password):
                        token = jwt.encode({
                            'user': user.email,
                            'uuid': user.uuid,
                            'iat': datetime.utcnow()
                        },
                        app.config.get('SECRET_KEY'),
                        algorithm='HS256')
                        string_token = str(token)
                        return {
                            'status': 1,
                            'res': 'success',
                            'token': string_token
                        }, 200
                else:
                    return {
                            'status': 0,
                            'res': "Worker doesn't exist",
                        }, 401
            if login_type == 'admin' :
                user = Administrators.query.filter_by(email=email).first()
                if user:
                    if user.verify_password(password):
                        token = jwt.encode({
                            'user': user.email,
                            'uuid': user.uuid,
                            'iat': datetime.utcnow()
                        },
                        app.config.get('SECRET_KEY'),
                        algorithm='HS256')
                        string_token = str(token)
                        return {
                            'token': string_token
                        }, 200
                else:
                    return {
                            'error': "Admin doesn't exist",
                        }, 400
            else:
                return {
                            'error': "Admin doesn't exist",
                        }, 400
        else:
            return {
                            'error': "data not passed well",
                        }, 400

@signup.doc(
    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })
@signup.route('/auth/signup')
class Signup(Resource):
    #@signup.expect(schema.signupdata)
    def post(self):
        signup_data = request.form
        signup_type = 'admin' 
        email = signup_data.get('email',None) 
        password = signup_data.get('password',None) 
        
        if email and password is None:
            return {
                    'error': 'Input data please',
                }, 400

        if signup_type == 'worker' :
            exuser = Worker.query.filter_by(email=email).first() 
            if exuser:
                return {
                    'status': 0,
                    'res': 'user exists',
                }, 400
            newworker = Worker(email=email,uuid=str(uuid.uuid4()))
            db.session.add(newworker)
            db.session.commit()
            newworker.passwordhash(password)
            db.session.commit()
            token = jwt.encode({
                'user': newworker.email,
                'uuid': newworker.uuid,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            return {
                'token': str(token),
            }, 200
        if signup_type == 'client' :
            exuser = Client.query.filter_by(email=email).first() 
            if exuser:
                return {
                    'error': 'user exists',
                }, 400
            newclient = Client(email=email,uuid=str(uuid.uuid4()))
            db.session.add(newclient)
            db.session.commit()
            newclient.passwordhash(password)
            db.session.commit()
            token = jwt.encode({
                'user': newclient.email,
                'uuid': newclient.uuid,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            return {
                'token': str(token)
            }, 200
        if signup_type == 'admin' :
            exuser = Administrators.query.filter_by(email=email).first() 
            if exuser:
                return {
                    'error': 'user exists',
                }, 400
            newadmin = Administrators(email=email,uuid=str(uuid.uuid4()))
            db.session.add(newadmin)
            db.session.commit()
            newadmin.passwordhash(password)
            db.session.commit()
            token = jwt.encode({
                'user': newadmin.email,
                'uuid': newadmin.uuid,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            return {
                'token': str(token)
            }, 200


            