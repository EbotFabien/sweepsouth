from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps 
from flask import abort, request, session,Blueprint
from datetime import datetime
from flask import current_app as app
from sqlalchemy import or_, and_, distinct, func
from project.api.models import Client,p_location,Administrators
from project import db, cache  #, logging

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
client1=Api( app=api, doc='/docs',version='1.4',title='Sweep API.',\
description='', authorizations=authorizations)
#implement cors

CORS(api, resources={r"/api/*": {"origins": "*"}})

client   = client1.namespace('/api/client', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

property_L=client.model('property_L', {
    'location': fields.String(required=True),
    'Type': fields.String(required=True),
})

View_client =client.model('View_client', {
    'id': fields.String(required=True),
    'first_name': fields.String(required=True),
    'second_name': fields.String(required=True),
    'uuid': fields.String(required=True),
    'gender': fields.String(required=True),
    'Date_birth': fields.String(required=True),
    'date_created': fields.String(required=True),
    'email': fields.String(required=True),
    'number': fields.String(required=True),
    'idcard': fields.String(required=True),
    'passport': fields.String(required=True),
    'locations': fields.List(fields.Nested(property_L))
})

Delete_client=client.model('Delete_client', {
    'id': fields.String(required=True),
})

edit_client =client.model('edit_client', {
    'first_name': fields.String(required=True),
    'second_name': fields.String(required=True),
    'gender': fields.String(required=True),
    'Date_birth': fields.String(required=True),
    'number': fields.String(required=True),
    'idcard': fields.String(required=True),
    'passport': fields.String(required=True),
})

View_location =client.model('View_location', {
    'id': fields.Integer(required=True),
    'location': fields.String(required=True),
    'Type': fields.String(required=True),
})


delete_location =client.model('Remove_location', {
    'id': fields.Integer(required=True)
})


@client.doc(
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
@client.route('/client')
class Data(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        client =Client.query.filter_by(uuid=data['uuid']).first()
        if client:
            return{
            "results":marshal(client,View_client)
            }, 200

        else:
            return {'res': 'User not found'}, 404

    @token_required
    @client.expect(Delete_client)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))#who has the right to delete a client 
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()

        if admin  is None:
            return {'res': 'This admin doesnt exist'}, 404#check this really well
        
        else:
            client=Client.query.filter_by(id=req_data['id']).first()
            client.visibility=False
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200


    @token_required
    @client.expect(edit_client)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))#who has the right to delete a worker 
        client =Client.query.filter_by(uuid=data['uuid']).first()

        if client is None:
            return {'res': 'This user doesnt exist'}, 404#check this really well
        
        else:
            client =Client.query.filter_by(uuid=data['uuid']).first()
            client.first_name=req_data['first_name']
            client.second_name=req_data['second_name']
            client.gender=req_data['gender']
            client.Date_birth=req_data['Date_birth']
            client.number=req_data['number']
            client.idcard=req_data['idcard']
            client.passport=req_data['passport']
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200





@client.doc(
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
@client.route('/client/location')
class Location(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        client = Client.query.filter_by(uuid=data['uuid']).first()
        if client  :
            location=p_location.query.filter_by(client_id=client.id).all()
            return{
                "results":marshal(location,View_location)
                }, 200

        else:
            return {'res': 'User not found'}, 404

    @token_required
    @client.expect(property_L) 
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        client =Client.query.filter_by(uuid=data['uuid']).first()

        if client:
            location=p_location(client_id=client.id,location=req_data['location'],Type=req_data['Type'])
            db.session.add(location)
            db.session.commit()
            return{
                "status":1,
                "res":"success"
                }, 200

        else:
            return {'res': 'User not found'}, 404


    @token_required
    @client.expect(delete_location)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        client =Client.query.filter_by(uuid=data['uuid']).first()

        if client  :
            location=p_location.query.filter(and_(p_location.id==req_data['id'],p_location.client_id==client.id)).first()#asdd and operator
            location.visibility=False
            db.session.commit()
            return{
                "status":1,
                "res":"success"
                }, 200
            

        else:
            return {'res': 'User not found'}, 404
    

@client.doc(
    security='KEY',
    params={ 
            'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
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
@client.route('/client/allclients')#can possibly get all client locations here thru a relationship
class All(Resource):
    @token_required
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            admin =Administrators.query.filter_by(uuid=data['uuid']).first()
            if admin:
                clients = Client.query.order_by(Client.date_created.desc()).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    #"next": next,
                    #"previous": previous,
                    "results": marshal(clients, View_client)
                }, 200

            else:
                return {'res': 'You must be an admin to access this page '}, 404