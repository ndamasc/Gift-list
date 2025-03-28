from flask import Blueprint, jsonify, request, abort, session
from app.models import User, Gift, ReservedGift, bcrypt
import jwt
import datetime
from app import db
from app.config import Config
api_bp = Blueprint('api', __name__)



@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    next_page = request.args.get('next_page')

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


    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
    
    for field in ['email', 'password_hash']:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    return jsonify(user.to_dict())


@api_bp.route('/users/<int:id>', methods=['DELETE'])            ### para deletar usuario
def delete_user(id):
    user = User.query.get(id)

    if not user:
        return jsonify({'error': 'User not found'}), 404  # Código 404 = não encontrado

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'}), 200

# Post routes
@api_bp.route('/show/gifts', methods=['GET'])
def get_gifts():
    gifts = Gift.query.order_by(Gift.id.desc()).all()
    return jsonify([gift.to_dict() for gift in gifts])

@api_bp.route('/gifts/<int:id>', methods=['GET'])
def get_gift(id):
    gift = Gift.query.get_or_404(id)
    return jsonify(gift.to_dict())

"""'''
    criando rotas de presentes

'''"""

@api_bp.route('/gifts', methods=['POST'])
def create_gift():
    data = request.get_json() or {}
    
    if 'gift_title' not in data:
        return jsonify({'error': 'gift title is required'}), 400
    
    gift = Gift(
        gift_title=data['gift_title'],
        image_path=data.get('image_path'),  # Pode ser opcional
        link=data.get('link'),  # Pode ser opcional
        reserved=data.get('reserved', False)  # Por padrão, não reservado
    )

    db.session.add(gift)
    db.session.commit()
    
    return jsonify(gift.to_dict()), 201

"""
    atualizar/alterar presente ja existente

"""

@api_bp.route('/gifts/<int:id>', methods=['PUT'])
def update_post(id):
    gift = Gift.query.get_or_404(id)
    data = request.get_json() or {}
    
    for field in ['gift_title', 'image_path', 'link', 'reserved']:
        if field in data:
            if field in data:
                setattr(gift, field, data[field])
    
    db.session.commit()
    return jsonify(gift.to_dict())

@api_bp.route('/gifts/<int:id>', methods=['DELETE'])
def delete_gift(id):
    gift = Gift.query.get_or_404(id)
    db.session.delete(gift)
    db.session.commit()
    return jsonify({'result': True})

# User posts
@api_bp.route('/users/<int:id>/gifts', methods=['GET'])
def get_user_gifts(id):
    user = User.query.get_or_404(id)
    reserved_gifts = ReservedGift.query.filter_by(user_id=id).all()

    gifts = [reservation.gift.to_dict() for reservation in reserved_gifts]

    return jsonify([gift.to_dict() for gift in gifts])

@api_bp.route('/users/reserve-gifts', methods=['POST'])
def reserve_gifts():

    data = request.get_json() or {}

    if 'user_id' not in data or 'gift_id' not in data:
        return jsonify({'error': 'User ID and Gift ID are required'}), 400
    
    user = User.query.get(data['user_id'])
    gift = Gift.query.get(data['gift_id'])

    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not gift:
        return jsonify({'error': 'Gift not found'}), 404
    if gift.reserved:
        return jsonify({'error': 'Gift is already reserved'}), 400

    # Criando a reserva
    reservation = ReservedGift(user_id=user.id, gift_id=gift.id)
    gift.reserved = True  # Atualiza o status do presente para reservado

    db.session.add(reservation)
    db.session.commit()

    return jsonify({'message': 'Gift reserved successfully', 'reservation': reservation.id}), 201

@api_bp.route('/user/logout')
def logout():
    session.pop('logged_user', None)
    return jsonify({'message': 'Logout efetuado com sucesso!'}), 200