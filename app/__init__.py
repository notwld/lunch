from flask import Flask
from app.models import db
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from app.routes.dashboard import dashboard
from app.routes.auth import auth
from app.routes.order import order
from app.routes.admin import admin
import os



def create_app():
    app = Flask(__name__,
                static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here' 
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    db.init_app(app)
    jwt = JWTManager(app)
    
    from app.models import Parent
    @login_manager.user_loader
    def load_user(user_id):
        return Parent.query.get(int(user_id))

    
    app.register_blueprint(dashboard, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(order, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    return app
