from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Replace with your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    deadline = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now() + timedelta(days=2))
    parent = db.relationship('Parent', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

class Parent(db.Model):
    __tablename__ = 'parents'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    orders = db.relationship('Order', back_populates='parent')

# Background task to check orders nearing the deadline
def check_near_deadline_orders():
    with app.app_context():
        now = datetime.utcnow()
        reminder_time = now + timedelta(days=1)

        # Find orders with deadlines 1 day away and status "Pending"
        near_deadline_orders = Order.query.filter(
            Order.deadline >= now,
            Order.deadline < reminder_time,
            Order.status == "Pending"
        ).all()

        for order in near_deadline_orders:
            # Send reminder email (leave the function implementation to the user)
            send_reminder_email(order.parent.email, order.id, order.total_cost, order.deadline)

        db.session.commit()

        print(f"{len(near_deadline_orders)} reminder emails sent for orders nearing deadlines.")

# Function to send reminder emails
def send_reminder_email(email, order_id, total_cost, deadline):
    # Replace this with your email-sending logic
    print(f"Reminder email sent to {email} for Order {order_id}. Total: ${total_cost:.2f}, Deadline: {deadline}")

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_near_deadline_orders, trigger="interval", hours=1)  # Runs every 1 hour
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
