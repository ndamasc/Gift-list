from flask import Blueprint, jsonify, request, abort
from app.models import User, Gift, bcrypt
import jwt
import datetime
from app import db
from app.config import Config
api_bp = Blueprint('api', __name__)



@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.check_user_credentials(data['email'], data['password'])

    if not user :
        return jsonify({'error': 'Invalid email or password'}), 401  # Código 401 = não autorizado

    return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
    

# User routes
@api_bp.route('/users', methods=['GET'])                    ### lista todos os usuarios do banco
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api_bp.route('/users/<int:id>', methods=['GET'])           ### pega um usuario especifico
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@api_bp.route('/users', methods=['POST'])                   ### cria usuario 
def create_user():
    data = request.get_json() or {}
    
    if 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    if 'password' not in data or not data['password'].strip():
        return jsonify({'error': 'A password is required'}), 400


    user = User(
        name=data['name'],
        email=data['email']
    )

    user.set_password(data['password'])

    if not user.check_email_is_valid(data['email']): 
        return jsonify({'error': 'Email is not in valid format'}), 400


    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
    
    for field in ['username', 'email', 'password_hash']:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    return jsonify(user.to_dict())

@api_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'result': True})

# Post routes
@api_bp.route('/posts', methods=['GET'])
def get_gifts():
    gifts = Gift.query.order_by(Gift.created_at.desc()).all()
    return jsonify([gift.to_dict() for gift in gifts])

@api_bp.route('/posts/<int:id>', methods=['GET'])
def get_gift(id):
    gift = Gift.query.get_or_404(id)
    return jsonify(gift.to_dict())

@api_bp.route('/posts', methods=['POST'])
def create_gift():
    data = request.get_json() or {}
    
    if not all(key in data for key in ('title', 'content', 'user_id')):
        return jsonify({'error': 'Title, content, and user_id are required'}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    gift = Gift(
        title=data['title'],
        content=data['content'],
        user_id=data['user_id']
    )
    
    db.session.add(gift)
    db.session.commit()
    
    return jsonify(gift.to_dict()), 201

@api_bp.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    gift = Gift.query.get_or_404(id)
    data = request.get_json() or {}
    
    for field in ['title', 'content', 'user_id']:
        if field in data:
            if field == 'user_id' and not User.query.get(data['user_id']):
                return jsonify({'error': 'User not found'}), 404
            setattr(gift, field, data[field])
    
    db.session.commit()
    return jsonify(gift.to_dict())

@api_bp.route('/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    gift = Gift.query.get_or_404(id)
    db.session.delete(gift)
    db.session.commit()
    return jsonify({'result': True})

# User posts
@api_bp.route('/users/<int:id>/posts', methods=['GET'])
def get_user_posts(id):
    user = User.query.get_or_404(id)
    gifts = Gift.query.filter_by(user_id=id).order_by(Gift.created_at.desc()).all()
    return jsonify([gift.to_dict() for gift in gifts])