from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps 
from flask import abort, request, session,Blueprint
from datetime import datetime
from flask import current_app as app
from sqlalchemy import or_, and_, distinct, func
from project import db, cache  #, logging
from project.api.models import Extras,Worker,Client,Administrators


authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}

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

api = Blueprint('api',__name__, template_folder='../templates')
extra1=Api( app=api, doc='/docs',version='1.4',title='Sweep API.',\
description='', authorizations=authorizations)
#implement cors

CORS(api, resources={r"/api/*": {"origins": "*"}})

extra  = extra1.namespace('/api/extra', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

Add_extra =extra.model('Add_extra', {
    'service_id': fields.String(required=True),
    'name': fields.String(required=True),
    'prices': fields.String(required=True)
})

View_extra =extra.model('View_extra', {
    'id': fields.String(required=True),
    'service_id': fields.String(required=True),
    'extra_name': fields.String(required=True),
    'prices': fields.String(required=True)
})  

Delete_extra =extra.model('Delete_extra', {
    'id': fields.String(required=True)        
})


@extra.doc(
    security='KEY',
    params={ },
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
@extra.route('/extra')
class Extra(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker = Worker.query.filter_by(uuid=data['uuid']).first()
        client =Client.query.filter_by(uuid=data['uuid']).first()
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()
        if worker or client or admin :
            extras=Extras.query.filter_by(visibility=True).all()
            return{
                "results":marshal(extras,View_extra)
                }, 200

        else:
            return {'res': 'User not found'}, 404

    @token_required
    @extra.expect(Add_extra) 
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()

        if admin is None:
            return {'res': 'Only workers are allowed to access this page'}, 404

        else:
            extra=Extras(service_id=req_data['service_id'],extra_name=req_data['name'],price=req_data['prices'])
            db.session.add(extra)
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200


    @token_required
    @extra.expect(Delete_extra)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()

        if admin is None:
            return {'res': 'Only workers are allowed to access this page'}, 404
        
        else:
            extra=Extras.query.filter_by(id=req_data['id']).first()
            extra.visibility=False
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200

                