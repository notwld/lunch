from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Parent(db.Model):
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Account Info
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Parent Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    
    # Contact Info
    home_phone = db.Column(db.String(15), nullable=True)
    cell_phone = db.Column(db.String(15), nullable=False)
    work_phone = db.Column(db.String(15), nullable=True)

    # Relationships
    children = db.relationship('Child', back_populates='parent', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<Parent {self.email}>"


class Child(db.Model):
    __tablename__ = 'children'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Child Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    county = db.Column(db.String(50), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    allergies = db.Column(db.Text, nullable=True)
    
    # Relationship
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    parent = db.relationship('Parent', back_populates='children')
    
    def __repr__(self):
        return f"<Child {self.first_name} {self.last_name}>"
