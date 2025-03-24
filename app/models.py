from datetime import datetime
import re
from flask_bcrypt import Bcrypt
from app import db

bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.utcnow)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    is_root = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    reservations = db.relationship('ReservedGift', back_populates='user', cascade='all, delete-orphan')

   
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_root': self.is_root,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'reservations': self.reservations

        }
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)  

    def check_email_is_valid(self, email):
        email_rgx = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_rgx, email) is not None
    
    def check_user_credentials(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        return None

class Gift(db.Model):
    __tablename__ = 'gifts'
    id = db.Column(db.Integer, primary_key=True)
    gift_title = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(250))
    link = db.Column(db.String(1000))
    reserved = db.Column(db.Boolean, default=False)

    reservations = db.relationship('ReservedGift', back_populates='gift', cascade='all, delete-orphan')
   

    def __repr__(self):
        return f'<Gift {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'gift_title': self.gift_title,
            'image_path': self.image_path,
            'link': self.link,
            'reserved': self.reserved
        }
    
class ReservedGift(db.Model):
    __tablename__ = 'reserved_gifts'
    id = db.Column(db.Integer, primary_key=True)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    gift_id = db.Column(db.Integer, db.ForeignKey('gifts.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', back_populates='reservations')
    gift = db.relationship('Gift', back_populates='reservations')