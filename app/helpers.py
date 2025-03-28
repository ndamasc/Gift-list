from flask import Blueprint, jsonify, request, abort, session
from app.models import User, Gift, bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators
from app import db
api_bp = Blueprint('api', __name__)


class UserForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Length(min=1, max=8)]),
    password = StringField('Senha', [validators.DataRequired(), validators.Length(min=1, max=8)])
   

