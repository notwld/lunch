from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

class Parent(UserMixin,db.Model):
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
    orders = db.relationship('Order', back_populates='parent', cascade='all, delete-orphan')

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
    grade = db.Column(db.String(20), nullable=False)
    allergies = db.Column(db.Text, nullable=True)

    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    school = db.relationship('School', back_populates='children')
    
    # Relationship
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    parent = db.relationship('Parent', back_populates='children')
    
    def __repr__(self):
        return f"<Child {self.first_name} {self.last_name}>"

class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # School Info
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    special_instructions = db.Column(db.Text, nullable=True)
    total_students = db.Column(db.Integer, nullable=True)
    # Relationships
    children = db.relationship('Child', back_populates='school', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<School {self.name}>"


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    deadline = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now() + timedelta(days=2))
    # Relationships
    parent = db.relationship('Parent', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    rating = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Order {self.id} - Total: {self.total_cost}>"

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)

    # Food Items
    dessert_name = db.Column(db.String(100), nullable=True)
    dessert_price = db.Column(db.Float, nullable=True, default=0.0)
    drink_name = db.Column(db.String(100), nullable=True)
    drink_price = db.Column(db.Float, nullable=True, default=0.0)
    entree_name = db.Column(db.String(100), nullable=True)
    entree_price = db.Column(db.Float, nullable=True, default=0.0)
    produce_name = db.Column(db.String(100), nullable=True)
    produce_price = db.Column(db.Float, nullable=True, default=0.0)
    side_name = db.Column(db.String(100), nullable=True)
    side_price = db.Column(db.Float, nullable=True, default=0.0)

    # Relationships
    order = db.relationship('Order', back_populates='order_items')
    child = db.relationship('Child', backref='order_items')

    @property
    def total_price(self):
        return (
            (self.dessert_price or 0) +
            (self.drink_price or 0) +
            (self.entree_price or 0) +
            (self.produce_price or 0) +
            (self.side_price or 0)
        )

    def __repr__(self):
        return f"<OrderItem Day: {self.day}, Total: ${self.total_price:.2f}>"

class MenuItem (db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    img_url = db.Column(db.String(255), nullable=True)
    cautions = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<MenuItem {self.name} - ${self.price:.2f}>"    
    
class Coupons(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    discount = db.Column(db.Float, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active')
    
    def __repr__(self):
        return f"<Coupon {self.code} - {self.discount}%>"
    

