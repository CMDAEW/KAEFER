import os

import os
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://flaskuser:flaskpassword@localhost/invoicing')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
