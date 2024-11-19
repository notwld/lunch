from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

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
    
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Item Info
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Entree, Side, Produce, Dessert, Drink
    dietary_info = db.Column(db.String(255), nullable=True)  # E.g., Vegan, Gluten-Free
    availability_dates = db.Column(db.Text, nullable=False)  # JSON list of dates (e.g., ["2023-11-20", "2023-11-21"])

    def __repr__(self):
        return f"<MenuItem {self.name}>"


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Order Info
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)  # When the order was placed
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")  # Pending, Paid, Completed

    # Relationships
    child = db.relationship('Child', backref='orders')
    parent = db.relationship('Parent', backref='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Order {self.id} - Total: {self.total_cost}>"


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Order Item Info
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships
    order = db.relationship('Order', back_populates='order_items')
    menu_item = db.relationship('MenuItem', backref='order_items')

    def __repr__(self):
        return f"<OrderItem {self.menu_item.name} x{self.quantity}>"


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Payment Info
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # E.g., Credit Card, PayPal
    status = db.Column(db.String(20), nullable=False, default="Success")  # Success, Failed

    # Relationship
    order = db.relationship('Order', backref='payments')

    def __repr__(self):
        return f"<Payment {self.id} - Amount: {self.amount_paid}>"


class FoodRating(db.Model):
    __tablename__ = 'food_ratings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Rating Info
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    review_date = db.Column(db.DateTime, nullable=False)

    # Relationships
    parent = db.relationship('Parent', backref='ratings')
    menu_item = db.relationship('MenuItem', backref='ratings')

    def __repr__(self):
        return f"<FoodRating {self.menu_item.name} - Rating: {self.rating}>"

class Cart(db.Model):
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    user = db.relationship('Parent', backref='carts', lazy=True)

    # Cart items
    cart_items = db.relationship('CartItem', backref='cart', lazy=True)

    def __init__(self, user_id,child_id):
        self.user_id = user_id
        self.child_id = child_id
        self.total_price = 0.0  # start with 0 price

    def calculate_total(self):
        self.total_price = sum([item.price for item in self.cart_items])
        db.session.commit()
        
    def get_cart_items(self):
        return self.cart_items
    

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    
    # Foreign keys to MenuItem
    entree_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    side_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    produce_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    dessert_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    drink_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    
    # Prices are now calculated from the MenuItem model
    entree_price = db.Column(db.Float, nullable=False, default=0.0)
    side_price = db.Column(db.Float, nullable=False, default=0.0)
    produce_price = db.Column(db.Float, nullable=False, default=0.0)
    dessert_price = db.Column(db.Float, nullable=False, default=0.0)
    drink_price = db.Column(db.Float, nullable=False, default=0.0)
    
    entree = db.relationship('MenuItem', foreign_keys=[entree_id], lazy=True)
    side = db.relationship('MenuItem', foreign_keys=[side_id], lazy=True)
    produce = db.relationship('MenuItem', foreign_keys=[produce_id], lazy=True)
    dessert = db.relationship('MenuItem', foreign_keys=[dessert_id], lazy=True)
    drink = db.relationship('MenuItem', foreign_keys=[drink_id], lazy=True)
    
    price = db.Column(db.Float, nullable=False)

    def __init__(self, cart_id, day, entree, side, produce, dessert, drink):
        self.cart_id = cart_id
        self.day = day
        self.entree_id = entree.id if entree else None
        self.side_id = side.id if side else None
        self.produce_id = produce.id if produce else None
        self.dessert_id = dessert.id if dessert else None
        self.drink_id = drink.id if drink else None
        
        # Calculate prices from menu items
        self.entree_price = entree.price if entree else 0.0
        self.side_price = side.price if side else 0.0
        self.produce_price = produce.price if produce else 0.0
        self.dessert_price = dessert.price if dessert else 0.0
        self.drink_price = drink.price if drink else 0.0
        
        self.price = self.entree_price + self.side_price + self.produce_price + self.dessert_price + self.drink_price
