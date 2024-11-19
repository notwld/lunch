from flask import Flask
from app.models import db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__,
                static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here' 

    db.init_app(app)
    jwt = JWTManager(app)

    # Import and register routes
    from app.routes.dashboard import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
