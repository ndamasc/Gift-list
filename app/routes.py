from flask import Blueprint, jsonify, request, session, url_for
from flask_mail import Mail, Message
import jwt
from app.models import User, Gift, ReservedGift, bcrypt
from app.email_utils import send_confirmation_email
from app.config import Config
from app.decorators import admin_required, token_required
import datetime
from app import db, mail

api_bp = Blueprint('api', __name__)

mail = Mail()

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    next_page = request.args.get('next_page')

    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.check_user_credentials(data['email'], data['password'])

    if not user :
        return jsonify({'error': 'Invalid email or password'}), 401  # Código 401 = não autorizado

    

    token = jwt.encode(
        { 
            'user_id' : user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        Config.SECRET_KEY,
        algorithm='HS256'
    )

    return jsonify({'message': 'Login successful', 'token': token, 'user': user.to_dict()}), 200
    

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
    
    if 'password' in data and data['password'].strip():
        user.set_password(data['password'])
    
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


"""
criando rota para add admin

"""

@api_bp.route('/create-admin', methods=['POST'])
def create_admin():
    data = request.get_json() or {}

    if 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    if 'password' not in data or not data['password'].strip():
        return jsonify({'error': 'A password is required'}), 400
    

    admin_user = User(
        name=data['name'],
        email=data['email'],
        is_root=True
    )

    if not admin_user.check_email_is_valid(data['email']):
        return jsonify({'error': 'Email format not valid'}), 400
    
    admin_user.set_password(data['password'])

    db.session.add(admin_user)
    db.session.commit()

    return jsonify({'message': 'Admin user created successfully', 'user': admin_user.to_dict()}), 201


### rota de recuperacao de senha




"""'''
    criando rotas de presentes

'''"""

@api_bp.route('/gifts', methods=['POST'])
@admin_required
def create_gift(current_user):
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

    return jsonify(gifts)

""" 
    usuario faz a reserva
"""

@api_bp.route('/users/reserve-gift', methods=['POST'])
@token_required
def reserve_gifts(current_user):

    data = request.get_json() or {}

    if 'gift_id' not in data:
        return jsonify({'error': 'Gift ID is required'}), 400

    gift = Gift.query.get(data['gift_id'])

    if not gift:
        return jsonify({'error': 'Gift not found'}), 404
    if gift.reserved:
        return jsonify({'error': 'Gift is already reserved'}), 400
    
    token = jwt.encode(
        {
            'gift_id': gift.id,
            'user_id': current_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    reservation = ReservedGift(
        user_id=current_user.id,
        gift_id=gift.id,
        confirmation_token=token,
        confirmed=False
    )

    db.session.add(reservation)
    db.session.commit()

    print(f"[DEBUG] Reserva criada: user_id={current_user.id}, gift_id={gift.id}, token={token}")


    confirm_url = url_for('api.confirm_reservation', token=token, _external=True)

    msg = Message('Confirme sua reserva',
                  sender='nathaliacolares20@gmail.com',
                  recipients=[current_user.email])
    
    msg.body = (
        f'Olá, {current_user.name}!\n\n'
        f'Clique no link abaixo para confirmar a reserva do presente:\n{confirm_url}\n\n'
        'Se não foi você, ignore este e-mail.'
    )

    mail.send(msg)

    return jsonify({'message': 'Gift reserved successfully. Check your email for confirmation.'}), 201


""" 
    usuario confirma a reserva
"""

@api_bp.route('/confirm-reservation/<token>', methods=['GET'])
def confirm_reservation(token):
    try:
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        gift_id = data['gift_id']
        user_id = data['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired!'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token!'}), 400

    gift = Gift.query.get(gift_id)
    user = User.query.get(user_id)

    if not gift:
        return jsonify({'error': 'Gift not found'}), 404
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if gift.reserved:
        return jsonify({'error': 'Gift is already reserved'}), 400
    
    print(f"[DEBUG] Tentando confirmar reserva: user_id={user.id}, gift_id={gift.id}, token={token}")

    # Criação da reserva
    reservation = ReservedGift.query.filter_by(user_id=user.id, gift_id=gift.id, confirmation_token=token, confirmed=False).first() 

    print(f"[DEBUG] Reservation encontrada: {reservation}") if reservation else print("[DEBUG] Nenhuma reserva encontrada.")
    
    if not reservation:
        return jsonify({'error': 'Reservation not found or already confirmed'}), 404

    reservation.confirmed = True
    gift.reserved = True

    db.session.commit()

    return jsonify({'message': 'Gift reservation confirmed!'}), 200


""" 
Usuario administrador
"""


@api_bp.route('/user/logout')
def logout():
    session.pop('logged_user', None)
    return jsonify({'message': 'Logout efetuado com sucesso!'}), 200