from flask_restplus import Namespace, Resource, fields
from project.api import apisec

apiinfo = apisec.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})


full_login =  apisec.model('full_login', {
    'email': fields.String(required=True, description="Email"),
    'password': fields.String(required=True, description="Users Password"),
    'login_type':fields.String(required=False, description="determine_login"),

})


signupdata = apisec.model('Signup', {
    'email': fields.String(required=True, description="Users phone number"),
    'password': fields.String(required=True, description="Users Email"),
    'signup_type':fields.String(required=True, description="Signup Type")
})
