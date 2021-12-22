from project import  db
from itsdangerous import  TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from sqlalchemy import ForeignKeyConstraint,ForeignKey,UniqueConstraint
import json
from werkzeug.security import generate_password_hash, check_password_hash



class Administrators(db.Model):
    __tablename__ = 'Administrators'

    id = db.Column(db.Integer,primary_key=True)
    first_name  = db.Column(db.String)	
    second_name = db.Column(db.String)
    uuid = db.Column(db.String(60), nullable=False)
    gender=db.Column(db.String)
    password = db.Column(db.String(60))
    visibility =db.Column(db.Boolean,default=True)
    email = db.Column(db.String,unique=True)#unique

    def __repr__(self):
        return '<Administrators %r>' %self.id
    
    def passwordhash(self, password_taken):
        self.password = generate_password_hash(password_taken)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class Client(db.Model):
    __tablename__ = 'Client'

    id = db.Column(db.Integer,primary_key=True)
    first_name  = db.Column(db.String)	
    second_name = db.Column(db.String)
    uuid = db.Column(db.String(60), nullable=False)
    gender=db.Column(db.String)
    Date_birth=db.Column(db.DateTime)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    email = db.Column(db.String,unique=True)#unique
    number = db.Column(db.String)
    idcard=db.Column(db.String)
    passport=db.Column(db.String)
    password = db.Column(db.String(60))
    visibility =db.Column(db.Boolean,default=True)
    Locations = db.relationship('p_location', backref = "clientlocations", lazy = True)
    
    
    def __repr__(self):
        return '<Client %r>' %self.id
    
    def passwordhash(self, password_taken):
        self.password = generate_password_hash(password_taken)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class Services(db.Model):
    __tablename__ = 'Services'

    id = db.Column(db.Integer,primary_key=True)
    service  = db.Column(db.String)	
    price=db.Column(db.Float)
    duration=db.Column(db.String)
    visibility =db.Column(db.Boolean,default=True)


    def __repr__(self):
        return '<Services %r>' %self.id


class Indoor_rates(db.Model):
    __tablename__ = 'Indoor_rates'

    id = db.Column(db.Integer,primary_key=True)
    service_id=db.Column(db.Integer, ForeignKey('Services.id'))	
    N_bed = db.Column(db.Integer)
    N_bath=db.Column(db.Integer)
    price=db.Column(db.Float)
    duration=db.Column(db.String)
    service_data = db.relationship(
        'Services',
        primaryjoin=(service_id == Services.id),
        backref=db.backref('extras', uselist=False), uselist=False)

    def __repr__(self):
        return '<Indoor_rates %r>' %self.id

class Worker(db.Model):
    __tablename__ = 'Worker'

    id = db.Column(db.Integer,primary_key=True)
    first_name  = db.Column(db.String)	
    second_name = db.Column(db.String)
    uuid = db.Column(db.String(60), nullable=False)
    gender=db.Column(db.String)
    Date_birth=db.Column(db.DateTime)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    email = db.Column(db.String,unique=True)#unique
    number = db.Column(db.String)
    idcard=db.Column(db.String)
    passport=db.Column(db.String)
    password = db.Column(db.String(60))
    visibility =db.Column(db.Boolean,default=True)
    services = db.relationship('W_services', backref = "wservices", lazy = True)
    location = db.relationship('W_location', backref = "wlocations", lazy = True)
    
    
    def __repr__(self):
        return '<Worker %r>' %self.id


    def passwordhash(self, password_taken):
        self.password = generate_password_hash(password_taken)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

class Extras(db.Model):
    __tablename__ = 'Extras'

    id = db.Column(db.Integer,primary_key=True)
    service_id=db.Column(db.Integer, ForeignKey('Services.id'))
    extra_name=db.Column(db.String)
    price=db.Column(db.Float)
    visibility =db.Column(db.Boolean,default=True)

    def __repr__(self):
        return '<Extras %r>' %self.id

class Comment(db.Model):
   __tablename__ = 'Comment'

   id = db.Column(db.Integer,primary_key=True)
   client_id=db.Column(db.Integer, ForeignKey('Client.id'))
   worker_id=db.Column(db.Integer, ForeignKey('Worker.id'))
   comment=db.Column(db.String)
   date=db.Column(db.DateTime(),default=datetime.utcnow)
   visibility =db.Column(db.Boolean,default=True)
   

   def __repr__(self):
        return '<Comment %r>' %self.id


class Location(db.Model):
   __tablename__ = 'Location'

   id = db.Column(db.Integer,primary_key=True)
   location=db.Column(db.String)
   admin_id=db.Column(db.Integer, ForeignKey('Administrators.id'))
   date_created=db.Column(db.DateTime(),default=datetime.utcnow)
   visibility =db.Column(db.Boolean,default=True)

   def __repr__(self):
        return '<Location %r>' %self.id


class W_location(db.Model):
   __tablename__ = 'W_location'

   id = db.Column(db.Integer,primary_key=True)
   location_id=db.Column(db.Integer, ForeignKey('Location.id'))
   worker_id=db.Column(db.Integer, ForeignKey('Worker.id'))
   visibility =db.Column(db.Boolean,default=True)

   def __repr__(self):
        return '<W_location %r>' %self.id


class W_services(db.Model):
   __tablename__ = 'W_services'

   id = db.Column(db.Integer,primary_key=True)
   service_id=db.Column(db.Integer, ForeignKey('Services.id'))
   worker_id=db.Column(db.Integer, ForeignKey('Worker.id'))
   visibility =db.Column(db.Boolean,default=True)

   def __repr__(self):
        return '<W_services %r>' %self.id


class p_location(db.Model):
   __tablename__ = 'p_location'

   id = db.Column(db.Integer,primary_key=True)
   client_id=db.Column(db.Integer, ForeignKey('Client.id'))
   location=db.Column(db.String)
   Type=db.Column(db.String)
   visibility =db.Column(db.Boolean,default=True)


   def __repr__(self):
        return '<p_location %r>' %self.id


class Booking(db.Model):
   __tablename__ = 'Booking'

   id = db.Column(db.Integer,primary_key=True)
   service_id=db.Column(db.Integer, ForeignKey('Services.id'))
   service_data = db.relationship(
        'Services',
        primaryjoin=(service_id == Services.id),
        backref=db.backref('services', uselist=False), uselist=False)

   extras_id=db.Column(db.Integer, ForeignKey('Extras.id'))
   extras_data = db.relationship(
        'Extras',
        primaryjoin=(extras_id == Extras.id),
        backref=db.backref('extras', uselist=False), uselist=False)

   location_id=db.Column(db.Integer, ForeignKey('Location.id'))
   worker_id=db.Column(db.Integer, ForeignKey('Worker.id'))
   client_id=db.Column(db.Integer, ForeignKey('Client.id'))
   property_id=db.Column(db.Integer, ForeignKey('p_location.id'))
   price=db.Column(db.Float)
   once=db.Column(db.Boolean)
   frequency=db.column(db.String)
   validate=db.Column(db.Boolean,default=False)
   discount=db.Column(db.String)
   duration=db.Column(db.String)
   date_time=db.Column(db.DateTime(),default=datetime.utcnow)
   status=db.Column(db.Boolean,default=False)
   visibility =db.Column(db.Boolean,default=True)


   def __repr__(self):
        return '<Booking %r>' %self.id

class Booking_location(db.Model):
    __tablename__ = 'Booking_location'

    id = db.Column(db.Integer,primary_key=True)
    location=db.Column(db.Integer, ForeignKey('p_location.id'))
    Booking_id=db.Column(db.Integer, ForeignKey('Booking.id'))

    def __repr__(self):
        return '<Booking_location %r>' %self.id

class receipt(db.Model):
    __tablename__ = 'receipt'

    id = db.Column(db.Integer,primary_key=True)
    receipt_no_=db.column(db.String)
    Booking_id=db.Column(db.Integer, ForeignKey('Booking.id'))
    visibility =db.Column(db.Boolean,default=True)

    def __repr__(self):
        return '<receipt %r>' %self.id


class worker_availability(db.Model):
    __tablename__ = 'worker_availability'

    id = db.Column(db.Integer,primary_key=True)
    Booking_id=db.Column(db.Integer, ForeignKey('Booking.id'))
    worker_id=db.Column(db.Integer, ForeignKey('Worker.id'))
    status=db.Column(db.Boolean,default=True)
    visibility =db.Column(db.Boolean,default=True)


    def __repr__(self):
        return '<worker_availability %r>' %self.id