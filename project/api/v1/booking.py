from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps 
from flask import abort, request, session,Blueprint
from datetime import datetime
from flask import current_app as app
from sqlalchemy import or_, and_, distinct, func
from project.api.models import Booking,worker_availability,Client,Worker,Location,Indoor_rates
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
booking1=Api( app=api, doc='/docs',version='1.4',title='Sweep API.',\
description='', authorizations=authorizations)
#implement cors

CORS(api, resources={r"/api/*": {"origins": "*"}})

booking  = booking1.namespace('/api/booking', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

View_booking =booking.model('View_booking', {
    'id': fields.String(required=True),
    'service_id': fields.String(required=True),
    'extras_id': fields.String(required=True),
    'client_id': fields.String(required=True),
    #'once': fields.Boolean(required=True),
    'price': fields.String(required=True),
    'status': fields.String(required=True),
    'worker_id': fields.String(required=True),
    'date_time': fields.String(required=True),
    'validate': fields.Boolean(required=True),
})

Add_booking =booking.model('Add_booking', {
    'service_id': fields.List(fields.Integer(required=True)), 
    'extra_id': fields.List(fields.Integer(required=True)),
    #'Once_regular': fields.List(fields.Boolean(required=True)),
    'Location_ID': fields.List(fields.Integer(required=True)),
    'Property_id': fields.List(fields.Integer(required=True)),
    'bedroom': fields.List(fields.Integer(required=False)),
    'bathroom': fields.List(fields.Integer(required=False)),
    #'Duration': fields.List(fields.String(required=True)),
    #'Frequency': fields.List(fields.String(required=True))
})

validate_booking=booking.model('validate_booking', {
    'id': fields.Integer(required=True),
    'worker': fields.Integer(required=True),
})


@booking.doc(
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
@booking.route('/booking')
class Data(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        Booking_id=Booking.query.all()

        if Booking_id:
            return{
            "results":marshal(Booking_id,View_booking)
            }, 200

        else:
            return {'res': 'No Booking  found'}, 404


    @booking.expect(Add_booking) 
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        client =Client.query.filter_by(uuid=data['uuid']).first()
        length=len(req_data['service_id'])
        if client :
        
            if all(len(lst) == length for lst in [req_data['extra_id'],req_data['Location_ID'],req_data['Property_id'],
                                                    #req_data['Once_regular'],req_data['Frequency'],req_data['Duration'],
                                                    req_data['bedroom'],req_data['bathroom']]):
                for i in req_data['Location_ID']:
                     check_location=Location.query.filter_by(id=i).first()
                     if check_location is None:
                         return{
                                "status":2,
                                "res":"This location is not yet available"
                                }, 200
                for ser,ext,loca,prop,bed,bath in zip(req_data['service_id'],req_data['extra_id']
                                                        ,req_data['Location_ID'],req_data['Property_id'],req_data['bedroom'],req_data['bathroom']):
                                                        #req_data['Once_regular'],req_data['Frequency'],req_data['Duration'],onc,freq,dur
                    check_location=Location.query.filter_by(id=loca).first()     
                    if ser == 1:
                        sevi=Indoor_rates.query.filter(and_(Indoor_rates.service_id==ser,Indoor_rates.N_bath==bath,Indoor_rates.N_bed==bed)).first()    

                        if check_location:            
                            booking=Booking(service_id=ser,extras_id=ext,location_id=loca,property_id=prop,client_id=client.id)
                            #once=req_data['Once_regular'],frequency=req_data['Frequency'],duration=req_data['Duration'])
                            db.session.add(booking)
                            booking.price = float(sevi.service_data.price) + float(booking.extras_data.price)
                            db.session.commit()
                            
                        
                    else:
                        if check_location:            
                            booking=Booking(service_id=ser,extras_id=ext,location_id=loca,property_id=prop,client_id=client.id)
                            #once=onc,frequency=freq,duration=dur)
                            db.session.add(booking)
                            booking.price = booking.service_data.price + booking.extras_data.price
                            db.session.commit()
                            
                return{
                        "status":1,
                        "res":"success"
                        }, 200
            else:
                return {'res': 'Booking not ordered'}, 404
        else:
            return {'res': 'User not found'}, 404



    
@booking.doc(
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
@booking.route('/booking/validate')
class validate(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        Booking_id=Booking.query.filter_by(status=True).all()

        if Booking_id:
            return{
            "results":marshal(Booking_id,View_booking)
            }, 200

        else:
            return {'res': 'No Booking  found'}, 404

    @booking.expect(validate_booking) 
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        worker =Worker.query.filter_by(id=req_data['worker']).first()#we have to validate but with a type of worker
        Booking_id=Booking.query.filter(and_(Booking.id==req_data['id'],Booking.status==False)).first()

        if worker:
            availability=worker_availability.query.filter(and_(worker_availability.worker_id==req_data['worker'],worker_availability.status==False)).first()
            if availability:
                return {'res': 'Worker is taken'}, 404
        
        if worker and Booking_id :
            Booking_id.status=True
            Booking_id.worker_id=worker.id
            Booking_id.validate=True
            db.session.commit()
            return{
                "status":1,
                "res":"success"
                }, 200 

        else:
            return {'res': 'No Booking  found'}, 404