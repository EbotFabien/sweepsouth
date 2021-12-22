from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from functools import wraps 
from flask import abort,request,session,Blueprint
from datetime import datetime
from flask import current_app as app    
from flask_cors import CORS
from project.api.models import Worker,W_location,W_services,Administrators,Location
from sqlalchemy import or_, and_, distinct, func
from project import db, cache

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
location1=Api( app=api, doc='/docs',version='1.4',title='Sweep API.',\
description='', authorizations=authorizations)
#implement cors
CORS(api, resources={r"/api/*": {"origins": "*"}})


location  = location1.namespace('/api/location', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')


locations=location.model('locations', {
    'id': fields.String(required=True),
    'location': fields.String(required=True),
    'admin_id': fields.String(required=True),
    'date_created': fields.String(required=True),
})

add_location=location.model('add_location', {
    'location': fields.String(required=True),

})

delete_location=location.model('delete_location', {
    'id': fields.String(required=True),
})

update_location=location.model('update_location', {
    'id': fields.String(required=True),
    'location': fields.String(required=True),
})

@location.doc(
    security='KEY',
    params={
        'id': 'Id of the Location',
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
        500: 'internal server error, please contact admin and report issue'
    })
@location.route('/location')
class Data(Resource):

    def get(self):
        if request.args:
            ID = request.args.get('id', None)
            Loca =Location.query.filter_by(id=int(ID)).first()
            if Loca:
                return{
                "results":marshal(Loca,locations)
                }, 200

            else:
                return {'res': 'User not found'}, 404

    @token_required
    @location.expect(delete_location)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))#who has the right to delete a worker 
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()

        if admin  is None:
            return {'res': 'This admin doesnt exist'}, 404#check this really well
        
        else:
            locat=Location.query.filter_by(id=req_data['id']).first()
            locat.visibility=False
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200


    @token_required
    @location.expect(update_location)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))#who has the right to delete a worker 
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()
        loca =Location.query.filter_by(id=req_data['id']).first()

        if loca is None:
            return {'res': 'This location doesnt exist'}, 404#check this really well
        
        else:
            loca.location=req_data['location']
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200

    @token_required
    @location.expect(add_location) 
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()

        if admin:
            location=Location(location=req_data['location'],admin_id=admin.id)
            db.session.add(location)
            db.session.commit()
            return{
                "status":1,
                "res":"success"
                }, 200

        else:
            return {'res': 'User not found'}, 404


@location.doc(
    security='KEY',
    params={
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
        500: 'internal server error, please contact admin and report issue'
    })
@location.route('/all/location')
class Data(Resource):

    def get(self):
        Loca =Location.query.all()
        if Loca:
            return{
            "results":marshal(Loca,locations)
            }, 200

        else:
            return {'res': 'User not found'}, 404