from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps 
from flask import abort, request, session,Blueprint
from datetime import datetime
from flask import current_app as app
from sqlalchemy import or_, and_, distinct, func
from project.api.models import Services,Worker,Client,Location,Administrators,Indoor_rates
from project import db, cache  #, loggin

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
services1=Api( app=api, doc='/docs',version='1.4',title='Sweep API.',\
description='', authorizations=authorizations)
#implement cors

CORS(api, resources={r"/api/*": {"origins": "*"}})

Service = services1.namespace('/api/services', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')


Add_service =  Service.model('Add_service', {
    'name': fields.String(required=True),
    'N_Bedrooms': fields.String(required=False),
    'N_Bathrooms': fields.String(required=False),
    'duration': fields.String(required=False),
    'price': fields.String(required=True),
})
View_service = Service.model('View_service', {
    'id': fields.Integer(required=True),
    'service': fields.String(required=True),
    'N_bed': fields.String(required=True),
    'N_bath': fields.String(required=True),
    'duration': fields.String(required=False),
    'prices': fields.String(required=True),
})

View_Indoor = Service.model('View_Indoor', {
    'id': fields.Integer(required=True),
    'service_id':fields.String(required=True),
    'N_bed':fields.String(required=True),
    'N_bath':fields.String(required=True),
    'price':fields.String(required=True),
    'duration':fields.String(required=True),

})

delete_service =Service.model('delete_service', {
    'id': fields.Integer(required=True)
})

Add_location =Service.model('Add_location', {
    'location_name': fields.String(required=True),
})

View_location =Service.model('View_location', {
    'id': fields.Integer(required=True),
    'location': fields.String(required=True),
})

delete_location =Service.model('Remove_location', {
    'id': fields.Integer(required=True)
})


@Service.doc(
    security='KEY',
    params={ 
        'Type': 'Type of service',
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
@Service.route('/service')
class Data(Resource):
    @token_required
    def get(self):
        if request.args:
            Type = request.args.get('Type', None)
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker = Worker.query.filter_by(uuid=data['uuid']).first()#check
        client =Client.query.filter_by(uuid=data['uuid']).first()
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()
        if worker or client or admin :
            if Type is not None:
               indoor=Indoor_rates.query.all()
               return{
                "results":marshal(indoor,View_Indoor)
                }, 200
            services=Services.query.filter_by(visibility=True).all()
            return{
                "results":marshal(services,View_service)
                }, 200

        else:
            return {'res': 'User not found'}, 404

    @token_required
    @Service.expect(Add_service) 
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()
        if admin is None:
            return {'res': 'Only admins are allowed to access this page'}, 404

        else:
            if req_data['N_Bedrooms'] is not None :
                if req_data['name'] == "indoor":
                    Service=Services(service=req_data['name'],duration=req_data['duration'],price=req_data['price'])
                    db.session.add(Service)
                    db.session.commit()
                    indoor=Indoor_rates(service_id=Service.id,N_bed=req_data['N_Bedrooms'],N_bath=req_data['N_Bathrooms'],price=req_data['price'],duration=req_data['duration'])
                    db.session.add(indoor)
                    db.session.commit()
                    return{
                        "status":1,
                        "results":'success'
                        }, 200
                        
                else:
                    Service=Services.query.filter_by(service="indoor").first()
                    indoor=Indoor_rates(service_id=Service.id,N_bed=req_data['N_Bedrooms'],N_bath=req_data['N_Bathrooms'],price=req_data['price'],duration=req_data['duration'])
                    db.session.add(indoor)
                    db.session.commit()
                    return{
                        "status":1,
                        "results":'success'
                        }, 200
            else:
                Service=Services(service=req_data['name'],duration=req_data['duration'],prices=req_data['price'])
                db.session.add(Service)
                db.session.commit()
                return{
                    "status":1,
                    "results":'success'
                    }, 200

    @token_required
    @Service.expect(delete_service)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        admin =Administrators.query.filter_by(uuid=data['uuid']).first()

        if admin is None:
            return {'res': 'Only admins are allowed to access this page'}, 404
        
        else:
            service=Services.query.filter_by(id=req_data['id']).first()
            service.visibility=False
            db.session.commit()
            return{
                "status":1,
                "results":'success'
                }, 200







#specifiy the individual adding the name 