from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register routes
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')  ## se quiser tira
    
    # Register Swagger blueprint
    from app.swagger import create_swagger_blueprint
    create_swagger_blueprint(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return {
            "message": "Welcome to Flask SQLAlchemy API",
            "version": "1.0.0",
            "docs": "/api/docs",
            "endpoints": [
                "/api/users",
                "/api/users/<id>",
                "/api/posts",
                "/api/posts/<id>"
            ]
        }
    
    return app