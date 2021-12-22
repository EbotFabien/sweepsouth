from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from functools import wraps 
from flask import abort,request,session,Blueprint
from datetime import datetime
from flask import current_app as app    
from flask_cors import CORS
from project.api.models import Worker,W_location,W_services,Administrators
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
worker1=Api( app=api, doc='/docs',version='1.4',title='Sweep API.',\
description='', authorizations=authorizations)
#implement cors
CORS(api, resources={r"/api/*": {"origins": "*"}})


worker  = worker1.namespace('/api/worker', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

w_services=worker.model('w_services', {
    'service_id': fields.String(required=True),
})

w_location=worker.model('w_services', {
    'location_id': fields.String(required=True),
})

View_worker =worker.model('View_worker', {
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
    'services': fields.List(fields.Nested(w_services)),
    'locations': fields.List(fields.Nested(w_services))
})

edit_worker =worker.model('edit_worker', {
    'first_name': fields.String(required=True),
    'second_name': fields.String(required=True),
    'gender': fields.String(required=True),
    'Date_birth': fields.String(required=True),
    'number': fields.String(required=True),
    'idcard': fields.String(required=True),
    'passport': fields.String(required=True),
})

Delete_worker=worker.model('Delete_worker', {
    'id': fields.String(required=True),
})

D_services=worker.model('D_services', {
    'id': fields.String(required=True),
})
V_services=worker.model('V_services', {
    'service_id': fields.String(required=True),
})
All_services=worker.model('All_services', {
    'worker_id':fields.String(required=True),
    'service_id': fields.String(required=True),
})

@worker.doc(
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
@worker.route('/worker')
class Data(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker =Worker.query.filter_by(uuid=data['uuid']).first()
        if worker:
            return{
            "results":marshal(worker,View_worker)
            }, 200

        else:
            return {'res': 'User not found'}, 404

    @token_required
    @worker.expect(Delete_worker)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))#who has the right to delete a worker 
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()

        if admin  is None:
            return {'res': 'This admin doesnt exist'}, 404#check this really well
        
        else:
            worker=Worker.query.filter_by(id=req_data['id']).first()
            worker.visibility=False
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200


    @token_required
    @worker.expect(edit_worker)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))#who has the right to delete a worker 
        worker =Worker.query.filter_by(uuid=data['uuid']).first()

        if worker is None:
            return {'res': 'This user doesnt exist'}, 404#check this really well
        
        else:
            worker=Worker.query.filter_by(uuid=data['uuid']).first()
            worker.first_name=req_data['first_name']
            worker.second_name=req_data['second_name']
            worker.gender=req_data['gender']
            worker.Date_birth=req_data['Date_birth']
            worker.number=req_data['number']
            worker.idcard=req_data['idcard']
            worker.passport=req_data['passport']
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200






@worker.doc(
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
@worker.route('/worker/services')
class Location(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker =Worker.query.filter_by(uuid=data['uuid']).first()
        if worker  :
            location=W_services.query.filter_by(worker_id=worker.id).all()
            return{
                "results":marshal(location,V_services)
                }, 200

        else:
            return {'res': 'User not found'}, 404
    @token_required
    @worker.expect(w_services) 
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker =Worker.query.filter_by(uuid=data['uuid']).first()

        if worker:
            location=W_services(service_id=req_data['service_id'],worker_id=worker.id)
            db.session.add(location)
            db.session.commit()
            return{
                "status":1,
                "res":"success"
                }, 200

        else:
            return {'res': 'User not found'}, 404


    @token_required
    @worker.expect(D_services)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker =Worker.query.filter_by(uuid=data['uuid']).first()

        if worker  :
            location=W_services.query.filter(and_(W_services.id==req_data['id'],W_services.worker_id==worker.id)).first()#asdd and operator
            location.visibility=False
            db.session.commit()
            return{
                "status":1,
                "res":"success"
                }, 200
            

        else:
            return {'res': 'User not found'}, 404



@worker.doc(
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
@worker.route('/worker/allworkers')#can possibly get all worker services here thru a relationship
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
                workers = Worker.query.order_by(Worker.date_created.desc()).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                   # "next": next,
                    #"previous": previous,
                    "results": marshal(workers, View_worker)
                }, 200

            else:
                return {'res': 'User not found'}, 404
                

@worker.doc(
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
@worker.route('/worker/location')
class All_location(Resource):
    @token_required
    @worker.expect(w_services) 
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker =Worker.query.filter_by(uuid=data['uuid']).first()

        if worker:
            location=W_location(location_id=req_data['service_id'],worker_id=worker.id)
            db.session.add(location)
            db.session.commit()
            return{
                "status":1,
                "res":"success"
                }, 200

        else:
            return {'res': 'User not found'}, 404

