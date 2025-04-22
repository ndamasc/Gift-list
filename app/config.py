import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'AFHdsg%^9263^G6d72hhoiak)00')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://gift_list:cXlwjrjvnMnM@localhost:5432/gift_list')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False

    # MAIL_SERVER = os.getenv('MAIL_SERVER')
    # MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    # #MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    # MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    # MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='colares.sky@gmail.com'
    MAIL_PASSWORD='szoxwrwrrniytcyf'
