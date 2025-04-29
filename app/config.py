import os
from dotenv import load_dotenv
from dataclasses import dataclass


PROJECT_STAGE = os.environ.get('PROJECT_STAGE', 'dev')

if PROJECT_STAGE == 'dev':
    load_dotenv(dotenv_path='.env')
else:
    load_dotenv(dotenv_path='.env.prod')

@dataclass(frozen=True)
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USE_SSL =  os.getenv('MAIL_USE_SSL')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
