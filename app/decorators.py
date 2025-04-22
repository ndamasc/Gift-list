from functools import wraps
from flask import request, jsonify
from app.models import User
import jwt
from app.config import Config

def admin_required(f):
    @token_required
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if not current_user or not current_user.is_root:
            return jsonify({'error': 'Acesso negado: apenas administradores'}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token malformado'}), 401

        if not token:
            return jsonify({'error': 'Token ausente'}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        return f(current_user, *args, **kwargs)
    return decorated