import os

basedir= os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY='FABIENCLASSIC'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sweepsouth.sqlite') #"postgresql+psycopg2://postgres:1234@localhost/sweepsouth"
    MAIL_SERVER ='smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS =True
    MAIL_USERNAME = 'touchone0001@gmail.com'
    MAIL_PASSWORD = 'onetouch000100'
    SQLALCHEMY_TRACK_MODIFICATIONS = True 
    LANGUAGES = ['en', 'fr', 'arb', 'por']
    RESTPLUS_VALIDATE = True
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True
    SWAGGER_UI_DOC_EXPANSION = None
    RESTPLUS_MASK_SWAGGER = True
    RESTPLUS_VALIDATE = True
    #UPLOAD_FOLDER=#os.getcwd()+'\\data_base_\\static\\files'
    DEBUG = True



class Development(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000

class Production(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 80

 
config = {
    'dev': Development,
    'prod': Production,
    'default': Development
}